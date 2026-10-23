cmake_minimum_required(VERSION 3.8)
project(my_turtle_interfaces)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)

# List the exact 3 files you just created
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/Posetarget.msg"
  "srv/Setspeed.srv"
  "action/Gotopose.action"
)

ament_package()
