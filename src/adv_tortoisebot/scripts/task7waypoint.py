#! /usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseWithCovarianceStamped, PoseStamped
import time
class NavWaypoint(Node):

    def __init__(self):
        super().__init__('waypoint_navigation')
        self.get_logger().info("the way point following node is ucessfully established")
        self.client = ActionClient(self, NavigateToPose, '/navigate_to_pose')
        self.initpose = self.create_publisher(PoseWithCovarianceStamped, '/initialpose', 10)
        self.points = [[4.0,-2.0,1.0,0.0], [5.0,1.0,0.0,1.0], [2.0,4.0,0.0,1.0], [-2.0,4.0,0.0,1.0], [-4.5,0.0,0.0,1.0]]
        self.wait_times = [3,5,2,4,3,0]
        
    def set_initial(self,pose):
        initial = PoseWithCovarianceStamped()
        initial.header.frame_id = 'map'
        initial.header.stamp = self.get_clock().now().to_msg()

        initial.pose.pose.position.x = pose[0]
        initial.pose.pose.position.y = pose[1]

        initial.pose.pose.orientation.w = pose[2]
        initial.pose.pose.orientation.z = pose[3]

        self.get_logger().info("Setting Initial Pose...")
        for _ in range(5):
            self.initpose.publish(initial)
            time.sleep(0.5)

    def tothepose(self,pose):
        goal = NavigateToPose.Goal()
        goal.pose = pose
        future = self.client.send_goal_async(goal)
        rclpy.spin_until_future_complete(self,future=future)
        goal_handle = future.result()
        
        if not goal_handle:
            self.get_logger().error("Goal rejected")
            return
        
        self.get_logger().info("Navigating to the pos..")
        result_future = goal_handle.get_result_async()

        rclpy.spin_until_future_complete(self, result_future)
        result = result_future.result()

        if result is not None:
            self.get_logger().info("Goal reached successfully!")
        else:
            self.get_logger().error("Failed to get result")


def main(args = None):
    rclpy.init(args=args)
    node = NavWaypoint()

    initial = [0.0,0.0,1.0,0.0]
    node.set_initial(initial)
    node.get_logger().info("done initializing!")
    time.sleep(2)

    node.client.wait_for_server()
    node.get_logger().info("Navigation_stack is running!!")
    
    points = node.points.copy()
    wait_times = node.wait_times.copy()

    points.append(initial)
    pos = []
    # Go to our demos first goal pose
    for p in points:
        goal_pose = PoseStamped()
        goal_pose.header.frame_id = 'map'
        goal_pose.header.stamp = node.get_clock().now().to_msg()
        goal_pose.pose.position.x = p[0]
        goal_pose.pose.position.y = p[1]
        goal_pose.pose.orientation.w = p[2]
        goal_pose.pose.orientation.z = p[3]
        pos.append(goal_pose)
   
    loop_time = time.time()
    for i, po in enumerate(pos):
        start = time.time()
        node.tothepose(po)
        end = time.time()

        node.get_logger().info(f"pose went {i+1}")
        node.get_logger().info(f"time taken: {end - start:.2f} sec")

        if i < len(wait_times):
            node.get_logger().info(f"Waiting {wait_times[i]} sec")
            time.sleep(wait_times[i])
    node.get_logger().info(f"Total travel time: {time.time() - loop_time:.2f} sec")
    rclpy.shutdown()    

if __name__ == '__main__':
    main()