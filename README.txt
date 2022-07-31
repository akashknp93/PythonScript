Steps to run the script

1. Copy the script to any one of the node /home/support

2. To apply the gflags run the below command from cohesity CLI
-> python storage_issue_gflags.py --username=<iris_username> --password='<iris_password' --action=apply

3. To remove the gflags
-> python storage_issue_gflags.py --username=<iris_username> --password='<iris_password' --action=remove

-> Reason can be modified by appending the command with --reason=<reason>, by default reason will be space_issue

-> Please note, the script will ask the user to enter Y/N for below questions as below gflags are not required on all the clusters. Remaining gflags will be applied by default
Update Healer Priority Gflags?(Y/N):
Update Group Physical Storage Reporter Gflag?(Y/N):
Update max disk utilization Gflag?(Y/N):

-> Previous gflags will be auto saved and file location will be printed at the end

-> Apollo restart recommendation using iris_cli will be printed at the end because few gflags needs restart