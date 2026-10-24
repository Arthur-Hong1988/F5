# Edit by Arthur
import sys
import bigsuds


if __name__ == "__main__":
    # host = sys.argv[1]
    # name = sys.argv[2:]

    name = sys.argv[1:]
    hostip = ("30.95.0.33", "30.95.0.34", "30.127.0.33", "30.127.0.34", "30.159.0.30", "30.159.0.31")
    for host in hostip:
        api = bigsuds.BIGIP(host, username="admin", password="Ad@1hblsqt")
        api.LocalLB.Class.add_string_class_member([{'name': 'allow_domain', 'member': name}])
        api.LocalLB.Class.set_string_class_member_data_value([{'name': 'allow_domain', 'member': name}], [name])

    ret = api.LocalLB.Class.get_string_class(['allow_domain'])
    print("Current List:")
    print(ret)
