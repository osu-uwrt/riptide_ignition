import launch
from launch.launch_description import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction, GroupAction, ExecuteProcess
from launch.launch_description_sources import AnyLaunchDescriptionSource
from launch.actions import IncludeLaunchDescription
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node, PushRosNamespace
from launch.substitutions import LaunchConfiguration as LC
import os
import xacro

# evaluates LaunchConfigurations in context for use with xacro.process_file(). Returns a list of launch actions to be included in launch description
def evaluate_xacro(context, *args, **kwargs):
    robot = LC('robot').perform(context)
    debug = LC('debug').perform(context)
    world = "lake"
    # world = LC('world').perform(context) uncomment this line if the world is not named "lake"
    x = LC('x').perform(context)
    y = LC('y').perform(context)
    z = LC('z').perform(context)
    roll = LC('roll').perform(context)
    pitch = LC('pitch').perform(context)
    yaw = LC('yaw').perform(context)

    modelPath = launch.substitutions.PathJoinSubstitution([
        get_package_share_directory('riptide_descriptions2'),
        'robots',
        robot + '.xacro'
    ]).perform(context)

    print('using model definition', modelPath)

    xacroData = xacro.process_file(modelPath,  mappings={'debug': debug, 'namespace': robot, 'inertial_reference_frame':'world'}).toxml()
    xacroFilePath = os.path.join(
        '/tmp',
        '{}.xml'.format(robot)    
    )
    
    f = open(xacroFilePath, "w")
    f.write(xacroData)
    f.close()

    print('Converted model path', xacroFilePath)

    # URDF spawner
    urdf_spawner = ExecuteProcess(
        cmd=["ign", "service", "-s", "/world/{}/create".format(world), "--reqtype", "ignition.msgs.EntityFactory", "--reptype", "ignition.msgs.Boolean", "--timeout", "5000", "--req", "'sdf_filename:", "\"/tmp/{}.xml\",".format(robot), "name:", "\"{}\"'".format(robot)],
        output='both',
        shell=True
    )
   
    args=('-gazebo_namespace /gazebo '
        '-x %s -y %s -z %s -R %s -P %s -Y %s -entity %s -file %s' 
        %(x, y, z, roll, pitch, yaw, robot, xacroFilePath)).split()

    robot_state_publisher = Node(
        name = 'robot_state_publisher',
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output = 'screen',
        parameters=[{'robot_description': xacroData}], # Use subst here
    )

    # Message to tf
    message_to_tf_launch = os.path.join(
        get_package_share_directory('uuv_assistants'),
        'launch',
        'message_to_tf.launch'
    )

    message_to_tf_launch = IncludeLaunchDescription(
            AnyLaunchDescriptionSource(message_to_tf_launch),
            launch_arguments=[
                ('namespace', robot),
                ('world_frame', 'world'),
                ('child_frame_id', '/' + robot + '/base_link')
            ]
        )


    return [
        GroupAction([
            PushRosNamespace(robot), 
            robot_state_publisher,
            urdf_spawner
        ]),
        message_to_tf_launch
    ]
    
    
def start_ignition(context, *args, **kwargs):
    world = LC('world').perform(context) #IF WORLD IS NOT NAMED LAKE, UNCOMMENT THIS LINE AND IT SHOULD (HOPEFULLY) WORK
    riptide_ignition2_dir = get_package_share_directory("riptide_ignition2")
    world_path_full = os.path.join(riptide_ignition2_dir, "worlds", world)
    print("Using world file " + world_path_full + ".world")
    
    start_ignition = ExecuteProcess(
        cmd = ['ign', 'gazebo', '{}.world'.format(world_path_full)],
        output='both',
        shell=True
    )
    
    return [ start_ignition ]

def generate_launch_description():
    # Message to tf
    sensor_remap = os.path.join(
        get_package_share_directory('riptide_gazebo2'),
        'launch',
        'sensor_remap.launch.py'
    )

    return LaunchDescription([
        DeclareLaunchArgument('robot', default_value='tempest', description='name of the robot to spawn'),
        DeclareLaunchArgument('debug', default_value='0', description='whether to put gazebo into debug mode'),
        DeclareLaunchArgument('world', default_value='lake', description='The name of the world to launch'),
        DeclareLaunchArgument('x', default_value='0.0', description="X coordinate of the vehicle's initial position (in ENU)"),
        DeclareLaunchArgument('y', default_value='0.0',  description="Y coordinate of the vehicle's initial position (in ENU)"),
        DeclareLaunchArgument('z', default_value='0.0',  description="Z coordinate of the vehicle's initial position (in ENU)"),
        DeclareLaunchArgument('roll', default_value='0.0', description="Z coordinate of the vehicle's initial position (in ENU)"),
        DeclareLaunchArgument('pitch', default_value='0.0', description="Z coordinate of the vehicle's initial position (in ENU)"),
        DeclareLaunchArgument('yaw', default_value='0.0', description="Z coordinate of the vehicle's initial position (in ENU)"),
        OpaqueFunction(function=start_ignition),
        OpaqueFunction(function=evaluate_xacro),
        IncludeLaunchDescription(
            AnyLaunchDescriptionSource(sensor_remap),
            launch_arguments=[
                ('robot', LC('robot')),
            ]
        )
    ]) 

