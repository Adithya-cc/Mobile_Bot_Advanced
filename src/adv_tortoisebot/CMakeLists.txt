cmake_minimum_required(VERSION 3.8)
project(adv_tortoisebot)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclpy REQUIRED)
find_package(xacro REQUIRED)


if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()


install(DIRECTORY
  launch
  urdf
  rviz
  config
  world
  map
  maps
  DESTINATION share/${PROJECT_NAME}  # or ${PACKAGE_NAME}, but must match project/package
)

install(PROGRAMS
scripts/laser_pt_cloud.py
scripts/task7waypoint.py
DESTINATION lib/${PROJECT_NAME} 
)

ament_package()
