import re

from regexes import CAN_MSG_REGEX, BU_REGEX, BO_TX_BU_REGEX, CM_REGEX, VAL_REGEX
from utils import CAN_dbc, CAN_Signal, write_data_to_xlsx, CAN_Message

DBC_PATHS = [
    CAN_dbc(name="Sample DBC",
            dbc_path=r"sample_dbc.dbc")
]

PARSED_OBJECTS = {
}


def _process_CAN_Message(can_msg_data: str):
    msg_part, signal_part = can_msg_data
    id_msg, msg_name, msg_len, sender_name = re.findall(r"^BO_\s(\d+)\s(\w+):\s(\d+)\s(\w+)",
                                                        msg_part)[0]
    can_message = CAN_Message(msg_name=msg_name, msg_id=int(id_msg), msg_len=int(msg_len),
                              sender=sender_name, signals=[])

    signals = [el.replace("SG_", "") for el in signal_part.splitlines()]
    for signal in signals:
        can_signal = _process_CAN_Signal(signal)
        can_message.signals.append(can_signal)
    return can_message


def _process_CAN_Signal(signals: str):
    signal_name, signal_data = [el.strip() for el in signals.split(":")]
    signal_fields = signal_data.split(" ")

    bit_start_len_endian = signal_fields[0]
    scale_offset = signal_fields[1]
    min_max = signal_fields[2]
    unit = signal_fields[3]
    receiver = signal_fields[4]

    bit_start = bit_start_len_endian.split("|")[0]
    bit_len, endian, unsigned = re.findall(r"(\d+)@(\d+)([+-])", bit_start_len_endian.split("|")[1])[0]

    endianness = "little-endian" if endian else "big-endian"

    if unsigned[0] == "+":
        is_unsigned = True
    elif unsigned[0] == "-":
        is_unsigned = False
    else:
        raise ValueError("Unsigned[0] does not have proper value!")

    scale, offset = [el.strip().replace("(", "").replace(")", "") for el in scale_offset.split(",")]
    min_val, max_val = [el.strip().replace("[", "").replace("]", "") for el in min_max.split("|")]
    unit = unit.replace("\"", "")

    receivers = receiver.split(",")
    return CAN_Signal(signal_name=signal_name,
                      bit_start=int(bit_start),
                      bit_len=int(bit_len),
                      endianness=endianness,
                      unsigned=is_unsigned,
                      scale=float(scale), offset=float(offset), min=float(min_val), max=float(max_val),
                      unit=unit,
                      receivers=receivers)


def _process_signal_values(values: list):
    signal_val_dict = dict()
    for value in values:
        pattern = r'(\d+) (\w+) (.+)'
        match = re.match(pattern, value)

        if not match:
            raise ValueError("The input string does not match the expected format.")

        msg_id = int(match.group(1))
        signal_name = match.group(2)

        enum_part = match.group(3)
        pair_pattern = r'(\d+) "([^"]+)"'
        enum_data = re.findall(pair_pattern, enum_part)

        temp_dict = signal_val_dict.get(msg_id, dict())
        temp_dict[signal_name] = enum_data
        temp_dict[msg_id] = temp_dict[signal_name]

        signal_val_dict[msg_id] = temp_dict
    return signal_val_dict


def read_CAN_messages(dbc_name: str, dbc_text: str):
    temp_list = []
    can_msgs = re.findall(CAN_MSG_REGEX, dbc_text, flags=re.MULTILINE)
    for can_msg_data in can_msgs:
        can_message = _process_CAN_Message(can_msg_data)
        temp_list.append(can_message)
    return temp_list


def parse_dbcs(dbc_list):
    for can_dbc in dbc_list:
        try:
            PARSED_OBJECTS[can_dbc.name]
        except KeyError:
            PARSED_OBJECTS[can_dbc.name] = []

        with open(can_dbc.dbc_path) as f:
            dbc_text = f.read()

        # can_msgs = re.findall(CAN_MSG_REGEX, dbc_text, flags=re.MULTILINE)
        # bu = re.findall(BU_REGEX, dbc_text, flags=re.MULTILINE)
        # bo_tx_bu = re.findall(BO_TX_BU_REGEX, dbc_text, flags=re.MULTILINE)
        # comments = re.findall(CM_REGEX, dbc_text, flags=re.MULTILINE)
        values = re.findall(VAL_REGEX, dbc_text, flags=re.MULTILINE)

        PARSED_OBJECTS[can_dbc.name] = read_CAN_messages(can_dbc.name, dbc_text)
        signal_val_dict = _process_signal_values(values)

        for can_msg in PARSED_OBJECTS[can_dbc.name]:
            msg_signal_values = signal_val_dict.get(can_msg.msg_id)
            if msg_signal_values:
                for signal in can_msg.signals:
                    signal.enums = msg_signal_values.get(signal.signal_name)

        for can_msg in PARSED_OBJECTS[can_dbc.name]:
            for signal in can_msg.signals:
                print(signal.signal_name)
                print(signal.enums)

    for can_dbc in PARSED_OBJECTS:
        print("*" * 50)
        print(f"CAN DBC {can_dbc}")
        print("*" * 50)
        sig_separator = "-" * 5 + ">"
        for can_msg in PARSED_OBJECTS[can_dbc]:
            print(can_msg)
            for signal in can_msg.signals:
                print(sig_separator, signal)

    write_data_to_xlsx(r"dbc_output_new.xlsx", PARSED_OBJECTS)


if __name__ == "__main__":
    parse_dbcs(DBC_PATHS)
