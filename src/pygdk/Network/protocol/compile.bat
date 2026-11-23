set "curr_dir=%~dp0"
protoc --proto_path=%curr_dir% --python_out=%curr_dir%/gen --pyi_out=%curr_dir%/gen common.proto
protoc --proto_path=%curr_dir% --python_out=%curr_dir%/gen --pyi_out=%curr_dir%/gen scene.proto
protoc --proto_path=%curr_dir% --python_out=%curr_dir%/gen --pyi_out=%curr_dir%/gen client.proto