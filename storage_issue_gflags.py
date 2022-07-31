"""
Author: Akash Gupta
"""
import argparse, subprocess, time, datetime

parser = argparse.ArgumentParser()
parser.add_argument('-u', '--username', type=str, default='admin')
parser.add_argument('-p', '--password', type=str, default='admin')
parser.add_argument('-r', '--reason', type=str, default='storage_issue')
parser.add_argument('-a', '--action', type=str, default='apply')
args = parser.parse_args()
username = args.username
password = args.password
reason = args.reason
action = args.action.lower()
iris_command = "iris_cli --username=" + username + " --password='" + \
               password + "' "
gflag_command = iris_command + "cluster update-gflag reason=" + reason + \
               " effective-now=true service-name={} gflag-name={}"
if action == 'apply':
    gflag_command += " gflag-value={}"
elif action == 'remove':
    gflag_command += " clear=true"
else:
    print("\nPlease specify action as apply or remove\n")
    exit(0)


def run_shell_command(command):
    proc = subprocess.Popen(command, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, shell=True)
    out, err = proc.communicate()
    exit_code = proc.returncode
    return out, err, exit_code


def run_shell_command_with_timeout(command, timeout):
    err = "\niris_cli Credentials Validation failed, exiting\n"
    out = ""
    exit_code = 0
    proc = subprocess.Popen(command, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, shell=True)
    while timeout:
        time.sleep(1)
        if proc.poll() is not None:
            out, err = proc.communicate()
            exit_code = proc.returncode
            break
        timeout -= 1
    return out, err, exit_code


def validate_iris_creds():
    command = iris_command + "cluster info"
    out, error, exit_code = run_shell_command_with_timeout(command, 10)
    if error:
        print(error)
        exit(0)
    return


def copy_existing_gflags():
    time_now = int(time.time())
    curr_time = datetime.datetime. \
        fromtimestamp(time_now).strftime('%Y-%m-%d-%H-%M-%S')
    file_name = "/tmp/ls-gflags_" + curr_time
    command = iris_command + "cluster ls-gflags > " + file_name
    run_shell_command(command)

    return file_name


def update_gflag(service_name, gflag_name, gflag_value):
    if action == 'remove':
        command = gflag_command.format(service_name, gflag_name)
    else:
        command = gflag_command.format(service_name, gflag_name, gflag_value)
    print_command = command.split("' ")[1]
    print("\n{}\n".format(print_command))
    out, error, exit_code = run_shell_command(command)
    print(out)
    return


def restart_services(service_name):
    command = iris_command + "cluster restart-services service-names={}".\
        format(service_name)
    out, error, exit_code = run_shell_command(command)


def update_async_delete_gflags():
    update_gflag('bridge', 'bridge_magneto_use_unlink_directory_api', 'false')
    update_gflag('bridge', 'bridge_madrox_perform_async_directory_deletes',
                 'false')
    update_gflag('bridge', 'bridge_magneto_perform_async_directory_deletes',
                 'false')
    update_gflag('bridge_proxy', 'bridge_magneto_use_unlink_directory_api',
                 'false')
    update_gflag('bridge_proxy',
                 'bridge_magneto_perform_async_directory_deletes', 'false')
    return


def update_healer_priority_gflag():
    update_gflag('bridge', 'bridge_apollo_action_admctl_threshold', '64')
    update_gflag('bridge', 'bridge_admctl_snaptree_maintenance_threshold',
                 '40')
    update_gflag('apollo', 'apollo_mr_healer_urgency', '10')
    update_gflag('apollo', 'apollo_mr_replication_fixer_run_interval_secs',
                 '14400')
    update_gflag('apollo',
                 'apollo_cluster_storage_usage_critical_pct_threshold', '75')
    update_gflag('apollo', 'apollo_mr_master_job_cancellation_duration_secs'
                           '', '259200')
    update_gflag('apollo', 'apollo_cluster_storage_usage_high_pct_threshold'
                           '', '65')
    update_gflag('apollo', 'apollo_mr_replication_fixer_run_interval_secs',
                 '14400')
    update_gflag('apollo', 'apollo_mr_tier_rebalancer_run_interval_secs',
                 '43200')
    update_gflag('apollo', 'apollo_mr_master_job_action_exec_time_min_pct',
                 '95')
    update_gflag('apollo', 'apollo_mr_pipelines_to_run',
                 'Healer,Healer_FastSnapTree,TierRebalancer,'
                 'ReplicationFixer,ViewSnapTreeFixer')
    return


def update_storage_reporter_disable_gflag():
    update_gflag(
        'apollo',
        'apollo_mr_group_physical_storage_reporter_run_interval_secs', '-1')
    return


def update_morph_bricks_disable_gflag():
    update_gflag('apollo', 'apollo_mr_enable_morph_bricks_pipeline', 'false')
    return


def update_disable_ec_migrate_gflag():
    update_gflag('apollo', 'apollo_mr_min_ec_migrate_action_replica_bytes',
                 '0')


def update_max_disk_utilization_to_96_gflag():
    update_gflag('bridge', 'disk_selector_max_disk_util_pct', '96')
    return


def update_view_snaptree_fixer_back_to_back_gflag():
    update_gflag('apollo', 'apollo_mr_view_snaptree_fixer_run_interval_secs',
                 '0')
    return


def main():
    validate_iris_creds()
    healer_priority_gflag = raw_input("\nUpdate Healer Priority Gflags?("
                                      "Y/N): ").strip().lower()
    disable_storage_reporter = raw_input("\nUpdate Group Physical Storage "
                                         "Reporter Gflag?(Y/N): "
                                         "").strip().lower()
    max_disk_utilization_to_96 = raw_input("\nUpdate max disk "
                                           "utilization Gflag?(Y/N): "
                                           "").strip().lower()
    file_name = copy_existing_gflags()
    if healer_priority_gflag == 'y':
        update_healer_priority_gflag()
    update_async_delete_gflags()
    if disable_storage_reporter == 'y':
        update_storage_reporter_disable_gflag()
    update_morph_bricks_disable_gflag()
    update_disable_ec_migrate_gflag()
    if max_disk_utilization_to_96 == 'y':
        update_max_disk_utilization_to_96_gflag()
    update_view_snaptree_fixer_back_to_back_gflag()

    print("\nRestart Apollo service with 'iris_cli cluster restart-services "
          "service-names=apollo' if required\n")
    print("\nPrevious gflags saved in {}\n".format(file_name))
    return


if __name__ == '__main__':
    main()
