# Edit by Arthur
import sys
import bigsuds


if __name__ == "__main__":
    name = sys.argv[1:]
    hostip = ("30.95.0.33", "30.95.0.34", "30.127.0.33", "30.127.0.34", "30.159.0.30", "30.159.0.31")
    for host in hostip:
        api = bigsuds.BIGIP(host, username="admin", password="Ad@1hblsqt")
        api.LocalLB.Class.delete_string_class_member([{'name': 'allow_domain', 'member': name}])

