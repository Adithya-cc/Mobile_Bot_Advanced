#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2, LaserScan
from laser_geometry import LaserProjection
import sensor_msgs_py.point_cloud2 as pc2
from tf2_ros import Buffer, TransformListener
from tf2_sensor_msgs.tf2_sensor_msgs import do_transform_cloud


class Pathing(Node):
    def __init__(self):
        super().__init__('LaserPointCloud')
        self.get_logger().info('LaserPointCloud')
        self.merged =[]
        self.laser = LaserProjection()
        self.pub = self.create_publisher(PointCloud2,'/laser_point_cloud2', 10)
        self.pub_M = self.create_publisher(PointCloud2,'/merge_point_cloud2', 10)
        self.sub__ = self.create_subscription(LaserScan, '/scan',self.Lcall_back, 10)
        self.sub_dp = self.create_subscription(PointCloud2, '/depthcam/points', self.Dcall_back, 10)
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.Laser_cloud = self.Depth_cloud = None
    def Lcall_back(self, msg):
            self.Laser_cloud = self.laser.projectLaser(msg)
            self.pub.publish(self.Laser_cloud)
            self.merge()
    def Dcall_back(self, msg):
            self.Depth_cloud = msg
            self.merge()
    def merge(self):
         if self.Laser_cloud == None or self.Depth_cloud == None:
              return
         try:
            # Look up the transform from laser frame to camera frame
            # This aligns the "downwards" laser to the camera's perspective
            trans = self.tf_buffer.lookup_transform(
                self.Depth_cloud.header.frame_id,
                self.Laser_cloud.header.frame_id,
                rclpy.time.Time()
            )
            
            # Transform the laser cloud
            transformed_laser = do_transform_cloud(self.Laser_cloud, trans)
            
            # Now read points from the TRANSFORMED cloud
            lsd = list(pc2.read_points(transformed_laser, field_names=("x", "y", "z")))
            depd = list(pc2.read_points(self.Depth_cloud, field_names=("x", "y", "z")))
            
            merge_msg = pc2.create_cloud_xyz32(self.Depth_cloud.header, lsd + depd)
            self.pub_M.publish(merge_msg)

         except Exception as e:
            self.get_logger().error(f'TF2 Error: {e}')

def main(args=None):
    rclpy.init(args=args)
    nodes=Pathing() 

    rclpy.spin(nodes)
    rclpy.shutdown()

if __name__ == '__main__':
    main()