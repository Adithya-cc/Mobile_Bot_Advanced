import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, SetEnvironmentVariable, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    # Get the launch directory
    pkg_dis = get_package_share_directory('adv_tortoisebot')
    
    nav2_yaml = os.path.join(pkg_dis, 'config', 'nav2_params.yaml')
    map_file = os.path.join(pkg_dis, 'maps', 'map.yaml')
    #default_bt_xml_filename= os.path.join(get_package_share_directory('agv_proto'), 'config', 'navigate_w_replanning_and_recovery.xml')
    rviz_file = os.path.join(pkg_dis, "rviz", "task6.rviz")
    octomap_path = os.path.join(pkg_dis, "maps", "my_octomap.bt")
    #remappings = [('/cmd_vel', '/diffbot_base_controller/cmd_vel_unstamped'),('/odom','/odom_filtered')] #odom_filtered for sensor fusion only
    #remappings = [('/cmd_vel', '/diff_cont/cmd_vel_unstamped')]
    nav2_bringup_launch = os.path.join(
        get_package_share_directory('nav2_bringup'), 
        'launch', 
        'bringup_launch.py'
    )
    
    parameter = {'map':map_file, 'params_file': nav2_yaml,'use_sim_time':'true'}
    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([os.path.join(pkg_dis, 'launch', "gazebo.launch.py")])
            ),
        Node(
            package="rviz2",
            executable="rviz2",
            arguments= ['-d', rviz_file],
            condition= None
            ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(nav2_bringup_launch),
            launch_arguments=parameter.items()
        ),
        Node(
            package='octomap_server',
            executable='octomap_server_node',
            name='octomap_server',
            parameters=[{
                'octomap_path': octomap_path,
                'frame_id': 'map',
                'resolution': 0.05,
                'latched_publisher': True  # Note: Boolean values usually don't need quotes in Python dicts
            }]
        )
    ])