from service_announcer import ServiceAnnouncer


def main():
    announcer = ServiceAnnouncer()
    while True:
        print(announcer.receive_broadcasts())


if __name__ == "__main__":
    main()

