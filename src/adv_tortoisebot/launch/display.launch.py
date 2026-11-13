import os 
import xacro
from ament_index_python import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    pkg_name = "adv_tortoisebot"
    pkg = get_package_share_directory(pkg_name)
    xacro_fie = os.path.join(pkg, 'urdf', 'tortoise_bot.urdf.xacro')
    rviz_file = os.path.join(pkg, "rviz", "config.rviz")
    doc = xacro.process_file(xacro_fie)
    robt_desc = doc.toprettyxml(indent=' ')
    params = {'robot_description': robt_desc, 'use_sim_time': True}
    

    node_robot_state_publisher = Node(package='robot_state_publisher',
                                  executable='robot_state_publisher',
                                  output='both',
                                  parameters=[params])
    
    node_jsp = Node(
        package='joint_state_publisher_gui',
        executable= 'joint_state_publisher_gui'
    )
    
    node_rviz = Node(
        package="rviz2",
        executable="rviz2",
        arguments= ['-d', rviz_file],
        condition= None
    )

    return LaunchDescription([
        node_robot_state_publisher,
        #node_jsp,
        node_rviz
    ])
