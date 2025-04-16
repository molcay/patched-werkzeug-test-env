from datetime import datetime
from pathlib import Path


def _get_repeat_number(line):
    """2025-04-14 15:51:51,200 [I] [763842] - Repeat #9 completed!"""
    return line.split("#")[-1].split(" ")[0]


def _get_time(line):
    """2025-04-04 10:09:21,523 [I] [3995696] - x"""
    return line.split(" ")[1].split(",")[0]


def _get_file_name(line):
    """2025-04-04 10:09:21,523 [I] [3995696] - Executing the request for "v2.2.3" with the file "test-files/na_10chars_7.txt"..."""
    return line.split('" with the file "')[1].replace('"...', "").split("/")[1]


def _get_version(line):
    """2025-04-04 10:09:21,523 [I] [3995696] - Executing the request for "v2.2.3" with the file "test-files/na_10chars_7.txt"..."""
    return line.split('" with the file "')[0].split(" - ")[1].split('"')[1]


def _calculate_duration(end_time, start_time):
    end_time_object = datetime.strptime(f"2025-01-01 {end_time}", '%Y-%m-%d %H:%M:%S')
    start_time_object = datetime.strptime(f"2025-01-01 {start_time}", '%Y-%m-%d %H:%M:%S')
    return round((end_time_object - start_time_object).total_seconds())


def main(repeated = False):
    logfile = Path('logs/run_test.log')
    with logfile.open() as f:
        all_lines = f.read().splitlines()
    
    cases = []
    case_start, case_end = -1, -1
    for i in range(len(all_lines[:])):
        if " - " not in all_lines[i]:
            continue
        log_start = all_lines[i].split(' - ')[1]
        if repeated:
            if log_start.startswith("Repeat #") and "starting..." in log_start:
                case_start = i
            elif log_start.startswith("Repeat #") and "completed!" in log_start:
                case_end = i
        else:
            if log_start.startswith("Executing"):
                case_start = i
            elif log_start.startswith("Executed "):
                case_end = i

        if case_start != -1 and case_end != -1:
            cases.append(all_lines[case_start:case_end+1])
            case_start, case_end = -1,-1

    for case in cases:
        if repeated:
            repeat_line = case[0]
            repeat = _get_repeat_number(repeat_line)
            print(f"repeat #{repeat}")
        first_line = case[0] if not repeated else case[1]
        last_line = case[-1] if not repeated else case[-2]
        started_at = _get_time(first_line)
        completed_at = _get_time(last_line)
        file_name = _get_file_name(first_line)
        version = _get_version(first_line)
        duration = _calculate_duration(completed_at, started_at)
        print(file_name, version, started_at, completed_at, duration, sep=";")
        

if __name__=="__main__":
    main(True)
