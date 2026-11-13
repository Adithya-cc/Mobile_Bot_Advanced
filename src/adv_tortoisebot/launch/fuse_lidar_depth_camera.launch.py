import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, SetEnvironmentVariable, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_xml.launch_description_sources import XMLLaunchDescriptionSource

#ros2 run octomap_server octomap_server_node --ros-args -p octomap_path:=./src/adv_tortoisebot/maps/my_octomap.bt -p frame_id:=map -p resolution:=0.05 -p latched_publisher:=true

def generate_launch_description():
    # Get the launch directory
    pkg_dis = get_package_share_directory('adv_tortoisebot')
    
    nav2_yaml = os.path.join(pkg_dis, 'config', 'nav2_params.yaml')
    slam_yaml = os.path.join(pkg_dis, 'config', 'mapper_params_t5.yaml')

    map_file = os.path.join(pkg_dis, 'maps', 'map.yaml')
    #default_bt_xml_filename= os.path.join(get_package_share_directory('agv_proto'), 'config', 'navigate_w_replanning_and_recovery.xml')
    rviz_file = os.path.join(pkg_dis, "rviz", "task5.rviz")
    octomap_path = os.path.join(pkg_dis, "maps", "my_octomap.bt")
    #remappings = [('/cmd_vel', '/diffbot_base_controller/cmd_vel_unstamped'),('/odom','/odom_filtered')] #odom_filtered for sensor fusion only
    #remappings = [('/cmd_vel', '/diff_cont/cmd_vel_unstamped')]
    slamtool_launch = os.path.join(
        get_package_share_directory('slam_toolbox'), 
        'launch', 
        'localization_launch.py'
    )
    octomap_mapping = IncludeLaunchDescription(
            XMLLaunchDescriptionSource([os.path.join(pkg_dis, 'launch', "octomap_launch.xml")])
            )
    octomap_localization = Node(
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
    gazebo = IncludeLaunchDescription(
            PythonLaunchDescriptionSource([os.path.join(pkg_dis, 'launch', "gazebo.launch.py")])
            )
    nav2_bringup_launch = os.path.join(
        get_package_share_directory('nav2_bringup'), 
        'launch', 
        'navigation_launch.py'
    )
    parameter_s = {'map':map_file, 'slam_params_file': slam_yaml,'use_sim_time':'true'}
    parameter = {'map':map_file, 'slam_params_file': nav2_yaml,'use_sim_time':'true'}
    slam = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(slamtool_launch),
            launch_arguments=parameter_s.items()
        )    
    navigation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(nav2_bringup_launch),
        launch_arguments=parameter.items()
    )
    
    return LaunchDescription([
        gazebo,
        Node(
            package='adv_tortoisebot',
            executable='laser_pt_cloud.py',
            name='pttocloud',
            output='screen'),
        Node(
            package="rviz2",
            executable="rviz2",
            arguments= ['-d', rviz_file],
            condition= None
            ),
        slam,
        # navigation,
        octomap_localization,
    ])