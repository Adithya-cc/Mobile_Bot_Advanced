import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource

import xacro


def generate_launch_description():

    pkg_name = 'adv_tortoisebot'
    pkg_dec = get_package_share_directory(pkg_name)

    # ---------------------------------------------------------
    # Robot description
    # ---------------------------------------------------------

    xacro_file = os.path.join(
        pkg_dec,
        'urdf',
        'tortoise_bot.urdf.xacro'
    )

    world_file = os.path.join(
        pkg_dec,
        'world',
        'custom_obstacle_world.world'
    )

    doc = xacro.process_file(xacro_file)
    robot_desc = doc.toprettyxml(indent='  ')

    params = {
        'robot_description': robot_desc,
        'use_sim_time': True
    }

    # ---------------------------------------------------------
    # Robot State Publisher
    # ---------------------------------------------------------

    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='both',
        parameters=[params]
    )

    # ---------------------------------------------------------
    # Gazebo Sim
    # ---------------------------------------------------------

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('ros_gz_sim'),
                'launch',
                'gz_sim.launch.py'
            )
        ),
        launch_arguments={
            'gz_args': f'-r empty.sdf'
        }.items()
    )

    # ---------------------------------------------------------
    # Spawn robot
    # ---------------------------------------------------------

    spawn_entry = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic',
            'robot_description',
            '-name',
            'tortoise_bot'
        ],
        output='screen'
    )

    # ---------------------------------------------------------
    # Controllers
    # ---------------------------------------------------------

    diff_cont_node = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'diff_cont',
            '--controller-manager',
            '/controller_manager'
        ],
        parameters=[
            {'use_sim_time': True}
        ],
        output='screen'
    )

    joint_brod_node = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'joint_brod',
            '--controller-manager',
            '/controller_manager'
        ],
        parameters=[
            {'use_sim_time': True}
        ],
        output='screen'
    )
    bridge_params = os.path.join(
    get_package_share_directory('myrobot_gazebo'),
    'params',
    'myrobot.yaml')

    start_gazebo_ros_bridge_cmd = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '--ros-args',
            '-p',
            f'config_file:={bridge_params}',
        ],
        output='screen',)
    # ---------------------------------------------------------
    # Launch description
    # ---------------------------------------------------------

    return LaunchDescription([
        start_gazebo_ros_bridge_cmd,
        node_robot_state_publisher,
        gazebo,
        spawn_entry,
        diff_cont_node,
        joint_brod_node
    ])
