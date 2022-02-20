#Spawns the robot into Ignition.

ign service -s /world/default/create --reqtype ignition.msgs.EntityFactory --reptype ignition.msgs.Boolean --timeout 1000 --req 'sdf_filename: "/home/brach/osu-uwrt/riptide_software/src/riptide_ignition/models/lake/model.sdf", name: "lake"'
