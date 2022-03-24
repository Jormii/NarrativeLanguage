class IWhere:

    def where(self) -> str:
        raise NotImplementedError()

    @staticmethod
    def msg(msgs):
        if not isinstance(msgs, list):
            msgs = [msgs]

        array_msg = [""]
        for msg in msgs:
            array_msg.append("- {}".format(msg))

        return "\n".join(array_msg)
