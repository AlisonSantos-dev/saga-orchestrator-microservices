import os
import threading

GRADLE_COMMAND = "gradlew.bat" if os.name == "nt" else "./gradlew"

APPLICATIONS = [
    "order-service",
    "orchestrator-service",
    "product-validation-service",
    "payment-service",
    "inventory-service",
]

failed_builds = []


def build_application(app):
    print("Building application {}".format(app))
    exit_code = os.system("cd {} && {} build -x test".format(app, GRADLE_COMMAND))
    if exit_code == 0:
        print("Application {} finished building!".format(app))
    else:
        print("Application {} FAILED to build!".format(app))
        failed_builds.append(app)


def docker_compose_up():
    print("Running containers!")
    os.system("docker-compose up --build -d")
    print("Pipeline finished!")


def build_all_applications():
    print("Starting to build applications!")
    threads = []
    for app in APPLICATIONS:
        thread = threading.Thread(target=build_application, args=(app,))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()


def remove_remaining_containers():
    print("Removing all containers.")
    os.system("docker-compose down")
    containers = [c for c in os.popen("docker ps -aq").read().split("\n") if c]
    if len(containers) > 0:
        print("There are still {} containers created".format(containers))
        for container in containers:
            print("Stopping container {}".format(container))
            os.system("docker container stop {}".format(container))
        os.system("docker container prune -f")


if __name__ == "__main__":
    print("Pipeline started!")
    build_all_applications()
    if failed_builds:
        print("Pipeline aborted! Failed builds: {}".format(failed_builds))
    else:
        remove_remaining_containers()
        docker_compose_up()