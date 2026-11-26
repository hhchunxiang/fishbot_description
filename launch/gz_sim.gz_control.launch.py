import os
import launch
import launch_ros
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution, TextSubstitution
from launch.event_handlers import OnProcessExit

def generate_launch_description():
    robot_name_in_model = "fishbot"
    self_pkg_path = FindPackageShare("fishbot_description")
    world_path = PathJoinSubstitution([self_pkg_path, 'worlds', 'warehouse_world.sdf'])
    
    fishbot_model_path = PathJoinSubstitution([self_pkg_path, 'urdf', 'fishbot', 'fishbot.gz_control.urdf.xacro'])
    
    action_declare_arg_model_path = launch.actions.DeclareLaunchArgument(
        'model',
        default_value=fishbot_model_path,
        description='Path to model file to spawn'
    )

    robot_description = launch_ros.parameter_descriptions.ParameterValue(
        launch.substitutions.Command(['xacro ', launch.substitutions.LaunchConfiguration('model')]),
        value_type=str
    )


    robot_state_publisher_node = launch_ros.actions.Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description, 'use_sim_time': True}]
    )

    joint_state_publisher_node = launch_ros.actions.Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher'
    )

    launch_gz = launch.actions.IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([FindPackageShare("ros_gz_sim"), 'launch', 'gz_sim.launch.py'])
        ),
        launch_arguments={
            'gz_args': [TextSubstitution(text='-r -v 4 '), world_path]
        }.items()
    )

    spawn_entity_node = launch_ros.actions.Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', robot_name_in_model,
            '-topic', 'robot_description',
            '-z', '0.1'
        ],
        output='screen'
    )

    bridge_config_path = PathJoinSubstitution([self_pkg_path, 'config', 'bridge_config.yaml'])
    bridge_node = launch_ros.actions.Node(
            package="ros_gz_bridge",
            executable="parameter_bridge",
            parameters=[{'config_file': bridge_config_path}],
            output="screen",
    )

    rviz2_config_path = PathJoinSubstitution([self_pkg_path, 'config', 'fishbot_description.rviz'])
    rviz2_node = launch_ros.actions.Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz2_config_path])
        
    return launch.LaunchDescription([
        action_declare_arg_model_path,
        robot_state_publisher_node,
        launch_gz,
        spawn_entity_node,
        bridge_node,
        rviz2_node,
    ])
