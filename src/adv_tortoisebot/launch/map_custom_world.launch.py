import os
from launch import LaunchDescription
from ament_index_python import get_package_share_directory
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    pkg_name = "my_bot_sim"
    pkg = get_package_share_directory(pkg_name)
    urdf_file = os.path.join(pkg, 'urdf', 'tortoise_bot.urdf')
    world_path = os.path.join(pkg, 'worlds', 'custom_obstacle_world.world')
    my_slam_params = os.path.join(pkg, 'config', 'mapper_params_online_async.yaml')
    # Read URDF
    with open(urdf_file, 'r') as infp:
        robot_desc = infp.read()

    return LaunchDescription([
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': robot_desc}]
        ),
        IncludeLaunchDescription(PythonLaunchDescriptionSource([os.path.join(get_package_share_directory('gazebo_ros'),'launch', 'gazebo.launch.py' )]),
                                 launch_arguments=[('world', world_path)]),
        IncludeLaunchDescription(PythonLaunchDescriptionSource([os.path.join(pkg,'launch', 'visual.launch.py' )])),
        
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                os.path.join(get_package_share_directory('slam_toolbox'), 'launch', 'online_async_launch.py')
            ]),
            launch_arguments={
                'slam_params_file': my_slam_params
            }.items()),
        Node(package='teleop_twist_keyboard',
            executable='teleop_twist_keyboard',
            name='teleop_twist_keyboard',
            prefix='gnome-terminal --', # This opens a new window
            output='screen'),

        Node(
            package='gazebo_ros',
            executable='spawn_entity.py',
            arguments=[
                '-topic', 'robot_description',
                '-entity', 'tortoise_bot',
                '-x', '0.0',
                '-y', '0.0',
                '-z', '0.15'
            ],
            output='screen'
        )
        
    ])