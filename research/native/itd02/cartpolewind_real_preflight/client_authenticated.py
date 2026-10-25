"""Nonprivileged learner-side transport attacker and schema acceptance fixture.

This image receives NO original CartPoleWind source, Git checkout, Docker socket,
private wind marker, source libraries or episode control. No learning episodes.
"""
import json
import os
import pathlib
import socket
import time

ALLOW = {"observation", "reward", "terminated", "truncated"}


def demand(test, why):
    if not test:
        raise AssertionError("LEARNER_ISOLATION_FAIL_CLOSED:" + why)


def confirm_unprivileged_container():
    demand(os.geteuid() != 0, "ROOT_USER")
    for path in ("/sealed/source_original.py", "/sealed/private_canary.txt",
                 "/var/run/docker.sock", "/upstream/causal_gym/envs/cartpole_wind.py",
                 "/github/workspace/causal_gym/envs/cartpole_wind.py"):
        demand(not pathlib.Path(path).exists(), "SOURCE_VISIBLE_" + path)
        try:
            with open(path, "rb") as f:
                f.read(8)
        except OSError:
            pass
        else:
            raise AssertionError("PRIVATE_FILE_OPENED_" + path)
    try:
        with open("/learner_should_not_write", "w", encoding="ascii") as output:
            output.write("unsafe")
    except OSError:
        pass
    else:
        raise AssertionError("CLIENT_ROOT_FS_WRITABLE")
    demand(not pathlib.Path("/sealed/owner.py").exists(), "OWNER_EXECUTABLE_IN_CLIENT")
    demand("DOCKER_HOST" not in os.environ, "DOCKER_DAEMON_ENV_EXPOSED")


def send(file_in, file_out, message):
    file_out.write((json.dumps(message, sort_keys=True) + "\n").encode("ascii"))
    file_out.flush()
    data = file_in.readline(4096)
    demand(bool(data) and len(data) < 4096, "NO_BOUNDED_RESPONSE")
    obj = json.loads(data)
    demand(isinstance(obj, dict), "NONOBJECT_RESPONSE")
    return obj


def main():
    confirm_unprivileged_container()
    connection = None
    for attempt in range(30):
        try:
            connection = socket.create_connection(("source-owner", 8765), timeout=1)
            break
        except OSError:
            time.sleep(0.2)
    demand(connection is not None, "SOURCE_WORKER_UNREACHABLE")
    with connection:
        connection.settimeout(10)
        file_in, file_out = connection.makefile("rb"), connection.makefile("wb")
        greeting = send(file_in, file_out, {"op": "health"})
        demand(greeting == {"protocol":"synthetic-owner-wire-v1", "status":"ready",
                            "original_imports":1, "original_episodes":0, "protected_first_use":False},
               "SOURCE_OWNER_AUTHORITY_DRIFT")
        for action in (0, 1):
            public = send(file_in, file_out, {"op":"probe", "action":action})
            demand(set(public) == ALLOW, "PRIVILEGED_WIRE_FIELD")
            demand(public == {"observation":[0.1,-0.2,0.0,0.05],
                              "reward":0.0, "terminated":False, "truncated":False},
                   "SYNTHETIC_PROTOCOL_DRIFT")
        attacks = [
            {"op":"reset"}, {"op":"step","action":1}, {"op":"see"},
            {"op":"ctf_do"}, {"op":"do"}, {"op":"get_graph"},
            {"op":"wind"}, {"op":"source"}, {"op":"read_file", "path":"/sealed/source_original.py"},
            {"op":"probe", "action":0, "debug":True}, {"op":"probe", "action":True},
            {"op":"probe", "action":3}, {"op":"probe", "action":"0"},
            {"op":"probe","action":0,"wind":1.0},
            {"op":"health", "env":"private"}, {"op":"__dict__"},
            ["op", "probe"], {}, 17, None,
        ]
        for attack in attacks:
            denial = send(file_in, file_out, attack)
            demand(denial == {"error":"DENIED"}, "ATTACK_NOT_DENIED_" + repr(attack))
        closing = send(file_in, file_out, {"op":"quit"})
        demand(closing == {"status":"bye", "original_episodes":0}, "OWNER_TERMINATION")
    print("CARTPOLEWIND_CLIENT_DIFFERENT_READONLY_CONTAINER=PASS",flush=True)
    print("CARTPOLEWIND_PRIVATE_FILES_INACCESSIBLE=PASS",flush=True)
    print("CARTPOLEWIND_PROTOCOL_PRIVILEGED_REQUESTS_DENIED=" + str(len(attacks)),flush=True)
    print("CARTPOLEWIND_SYNTHETIC_TRANSPORT_ONLY=TRUE",flush=True)
    print("CARTPOLEWIND_ORIGINAL_ENV_EPISODES=0",flush=True)
    print("CARTPOLEWIND_SCIENTIFIC_GO=FALSE",flush=True)


if __name__ == "__main__":
    main()
