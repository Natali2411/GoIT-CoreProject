from typing import Tuple, List

from bot_helper.bot_helper.address import Address, ADDRESS_KEY_LIST
from prompt_toolkit import prompt

from bot_helper.bot_helper.address_book import AddressBook
from bot_helper.bot_helper.birthday import Birthday, DATE_FORMAT
from bot_helper.bot_helper.notes.note_book import NotesBook
from bot_helper.bot_helper.record import RecordAlreadyExistsException, Record
from bot_helper.bot_helper.save_data.save_on_disk import SaveAddressBookOnDisk
from bot_helper.bot_helper.utils.command_prompts import get_nested_completer
from bot_helper.bot_helper.utils.format_str import FormatStr

records = dict()
contacts = AddressBook(data_save_tool=SaveAddressBookOnDisk(address="address_book.json"))
notes = NotesBook(
    data_save_tool=SaveAddressBookOnDisk(address="notes_data.json")
)


def input_error(func: callable) -> callable:
    """
    Decorator that wraps the function to handle possible errors.
    :param func: Function that should be wrapped.
    :return: Wrapped function.
    """

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError as err:
            return f"There is no such key {err}. Type a correct name!"
        except ValueError as err:
            return f"Passed values are incorrect. The trace error is '{err}'"
        except IndexError as err:
            return f"Not all parameters have been passed. Check it, please."
        except RecordAlreadyExistsException as err:
            return err

    return wrapper


@input_error
def parse_cli_command(cli_input: str) -> Tuple[str, callable, List[str]]:
    """
    Method that parses the typed commands from CLI.
    :param cli_input: String from CLI.
    :return: Function name, function object and function arguments.
    """
    for command_name, func in COMMANDS.items():
        if cli_input.lower().startswith(command_name):
            return command_name, func, cli_input[len(command_name):].strip().split()
    return "unknown", unknown, []


@input_error
def hello() -> str:
    """
    Method that returns greeting to the user.
    :return: Greeting string.
    """
    return "How can I help you?"


@input_error
def add_contact(*args) -> str:
    """
    Method that adds user contacts to the AddressBook.
    :param args: Username and phone that should be stored.
    :return: Successful string about adding contact.
    """
    name = args[0]
    phone = args[1]
    birthday = None
    if len(args) > 2:
        birthday = args[2]
    rec = Record(name=name, birthday=birthday)
    rec.add_phone(phone_num=phone)
    contacts.add_record(rec)
    return f"The contact with name '{name}', '{phone}' and birthday: '{birthday}' has " \
           f"been successfully added"


@input_error
def delete_contact(*args) -> str:
    """
    Method that removes user contacts from the AddressBook.
    :param args: Username that should be deleted.
    :return: Successful string about deleting contact.
    """
    name = args[0]
    contacts.delete(name=name)
    return f"The contact with name '{name}' has been successfully deleted from the " \
           f"Address Book"


@input_error
def change_phone(*args) -> str:
    """
    Method that changes user contacts in the Address Book if such user exists.
    :param args: Username and phone that should be stored.
    :return: String with an information about changing phone number.
    """
    name = args[0]
    old_phone = args[1]
    new_phone = args[2]
    rec = contacts.find(name)
    if rec:
        rec.edit_phone(old_phone=old_phone, new_phone=new_phone)
        contacts.update_record(rec)
        return f"Phone number for contact '{rec.name.value}' has been successfully " \
               f"changed from '{old_phone}' to '{new_phone}'"
    else:
        raise ValueError(f"The contact with the name '{name}' doesn't exist in the "
                         f"Address Book. Add it first, please.")


@input_error
def update_birthday(*args) -> str:
    """
    Method that changes user birthday in the Address Book if such user exists.
    :param args: Username and birthday that should be stored.
    :return: String with an information about changing birthday.
    """
    name = args[0]
    new_birthday = args[1]
    rec = contacts.find(name)
    if rec:
        old_birthday = rec.birthday.value
        if rec.birthday.value == Birthday(new_birthday).value:
            return f"New birthday value for the user '{rec.name.value}' is equal to " \
                   f"the previous value"
        rec.add_birthday(birthday=new_birthday)
        contacts.update_record(rec)
        return f"Birthday for contact '{rec.name.value}' has been successfully " \
               f"changed from '{old_birthday}' to '{new_birthday}'"
    else:
        raise ValueError(f"The contact with the name '{name}' doesn't exist in the "
                         f"Address Book. Add it first, please.")


@input_error
def find_contact_phone(*args) -> str:
    """
    Method that returns phone number by passed username.
    :param args: Username whose phone number should be shown.
    :return: The string with user's phone number.
    """
    name = args[0]
    rec = contacts.find(name)
    if rec:
        phone_nums = [phone_num.value for phone_num in rec.phones]
        return f"'{rec.name.value}\'s' phone numbers: " + ", ".join(phone_nums)
    else:
        raise ValueError(f"The contact with the name '{name}' doesn't exist in the "
                         f"Address Book.")


@input_error
def show_all(*args) -> str:
    """
    Method that shows all users's information from the Address Book: name, phone numbers,
    address, email, birthday.
    :return: String with all phone numbers of all users.
    """
    record_num = None
    if args:
        record_num = int(args[0])
    records = contacts.iterator(record_num)
    return FormatStr.show_address_book(records)


def search_contact(*args) -> str:
    """
    Method that searches the full information about users by name, phone number, birthday,
    email address, address and returns info if a typed string is a part of user's name
    or phone.
    :return: String with all data of all found users.
    """
    search_phrase = args[0].strip()
    if len(search_phrase) < 2:
        raise ValueError("Searched phrase must have at least 2 symbols")
    records = contacts.search_contact(search_phrase=search_phrase)
    rec = []
    for dic in [i for i in records]:
        rec += [(dic["name"], dic["info"])]
    return FormatStr.show_address_book([rec])


@input_error
def add_phone(*args):
    """
    Method that adds phone for the contact in the AddressBook.
    :param args: Input parameters (name and phone).
    :return: String with information about adding a new phone.
    """
    name = args[0]
    phone = args[1]
    rec = contacts.find(name)
    if rec:
        rec.add_phone(phone)
        contacts.update_record(rec)
        return f"Phone for contact {rec.name.value} has been added successfully"
    else:
        raise ValueError(f"The contact with the name '{name}' doesn't exist in the "
                         f"Address Book. Add it first, please.")


@input_error
def add_address(*args):
    """
    Method adds address to the contact.
    :param args: Input arguments: country, city, street, house, apartment.
    :return: String with the added address.
    """
    name = args[0]
    address_str = ' '.join(list(args[1:]))
    address = address_str.split(', ')
    rec = contacts.find(name)
    if rec:
        rec.add_address(address)
        contacts.update_record(rec)
        return (f"Address: **{', '.join([addr for addr in address if addr])}** for "
                f"contact {rec.name.value} has been added successfully")
    else:
        raise ValueError(f"The contact with the name '{name}' doesn't exist in the "
                         f"Address Book. Add it first, please.")


@input_error
def add_email(*args):
    """
    Method adds email to the contact.
    :param args: Input arguments from console.
    :return: String with the information about adding email.
    """
    name = args[0]
    email = args[1]
    rec = contacts.find(name)
    if rec:
        rec.add_email(email)
        contacts.update_record(rec)
        return f"Email for contact {rec.name.value} has been added successfully"
    else:
        raise ValueError(f"The contact with the name '{name}' doesn't exist in the "
                         f"Address Book. Add it first, please.")


@input_error
def change_email(*args) -> str:
    """
    Method that changes user contacts in the Address Book if such user exists.
    :param args: Username and email that should be stored.
    :return: String with an information about changing email.
    """
    name = args[0]
    old_email = args[1]
    new_email = args[2]
    rec = contacts.find(name)
    if rec:
        rec.edit_email(old_email=old_email, new_email=new_email)
        contacts.update_record(rec)
        return f"Email for contact '{rec.name.value}' has been successfully " \
               f"changed from '{old_email}' to '{new_email}'"
    else:
        raise ValueError(f"The contact with the name '{name}' doesn't exist in the "
                         f"Address Book. Add it first, please.")

@input_error
def change_address(*args) -> str:
    """
    Method that changes user contacts in the Address Book if such user exists.
    :param args: Username and address that should be stored.
    :return: String with an information about changing adress.
    """
    name = args[0]
    new_address = [add.replace(",", "") for add in args[1:]]
    rec = contacts.find(name)
    if rec:
        DICT_ADDRESS = {
            "country": rec.address.country,
            "city": rec.address.city,
            "street": rec.address.street,
            "house": rec.address.house,
            "apartment": rec.address.apartment
        }

        old_address = rec.address
        rec_address = old_address.value.copy()

        if rec.address.get_addr_dict() == Address(new_address).get_addr_dict():
            return f"New address value for the user '{rec.name.value}' is equal to " \
                   f"the previous value"
        if new_address[0] in ADDRESS_KEY_LIST:
            rec_address[DICT_ADDRESS[new_address[0]]] = new_address[1]
            rec_address = [addr for addr in rec_address.values()]
            rec.add_address(rec_address)
            contacts.update_record(rec)
            return f"{new_address[0].capitalize()} for contact '{rec.name.value}' has " \
                   f"been successfully changed from " \
                   f"'{old_address.value[DICT_ADDRESS[new_address[0]]]}' " \
                   f"to '{new_address[1]}'"

        rec.add_address(address=new_address)
        contacts.update_record(rec)
        return f"Address for contact '{rec.name.value}' has been successfully " \
               f"changed from {old_address.value} to {rec.address.value}"
    else:
        raise ValueError(f"The contact with the name '{name}' doesn't exist in the "
                         f"Address Book. Add it first, please.")

@input_error
def change_name(*args) -> str:
    """
    Method that changes user contacts in the Address Book if such user exists.
    :param args: The old and new username that should be stored.
    :return: String with an information about changing name.
    """
    name = args[0]
    new_name = args[1]
    rec = contacts.find(name)
    if rec:
        rec.name.value = new_name
        contacts.delete(name)
        contacts.add_record(rec)
        return f"Name for contact '{name}' has been successfully" \
               f"changed from '{name}' to '{new_name}'"
    else:
        raise ValueError(f"The contact with the name '{name}' doesn't exist in the "
                         f"Address Book. Add it first, please.")


@input_error
def good_bye() -> str:
    """
    Method that returns "Good bye!" string.
    :return: "Good bye!" string.
    """
    return "Good bye!"


@input_error
def show_days_to_birthday(*args) -> str:
    """
    Method returns the number of days to the next client's birthday. The method
    returns the number of days without fractional part.
    :return: String with a number of days.
    """
    name = args[0]
    record = contacts.find(name)
    if record:
        days_to_birthday = record.days_to_birthday()
        return f"Days to the next birthday for the contact '{record.name.value}' is " \
               f"{days_to_birthday} days"
    else:
        raise ValueError(f"Contact with a name '{name}' doesn't exist in the Address "
                         f"Book")


@input_error
def upcoming_birthdays(*args) -> str:
    """
    Method that shows upcoming birthdays within a specified number of days.
    :param args: Number of days.
    :return: String with upcoming birthdays.
    """
    days_threshold = int(args[0])
    upcoming_birthdays = contacts.get_contacts_upcoming_birthdays(days_threshold)

    result_str = FormatStr.get_formatted_headers_birthdays()
    for contact in upcoming_birthdays:
        result_str += "{:<10} | {:<20} | {:<70} |\n".format(
            contact['name'], contact['info']['birthday'],
            contact['days_to_birthday'])

    result_str += "--------------------------+++-----------------------------------\n"
    return result_str


@input_error
def unknown() -> str:
    """
    Method can be called when was typed a command that can't be recognised.
    :return: String with the explanation that was typed incorrect command.
    """
    return "Unknown command. Try again."


def add_note(*args):
    """
    Method that adds a note.
    :param args: Input parameters (title, content, tags).
    :return: String indicating successful addition of a note.
    """
    if len(args) < 2:
        return "There is lack of parameters for 'add note' command." \
               "Check details with command 'help'."
    title = args[0]
    content = args[1]
    tags = list(args[2:])
    return notes.add_note(title=title, content=content, tags=tags)


def delete_note(*args):
    """
    Method that deletes a note.
    :param args: Input parameters (title).
    :return: String indicating successful deletion of a note.
    """
    if len(args) < 1:
        return "There is lack of parameters for 'delete note' command. " \
               "Check details with command 'help'."
    title = args[0]
    return notes.delete_note(title=title)


def show_all_notes() -> str:
    """
    Method that shows all notes.
    :return: String representing all available notes.
    """
    return notes.show_all_notes()


def search_note(*args):
    """
    Method that searches for a note.
    :param args: Input parameters (query, sort_by).
    :return: String representing the search result for a note.
    """
    if len(args) < 2:
        return "There is lack of parameters for 'search note' command. " \
               "Check details with command 'help'."
    query = args[1]
    sort_by = args[2]
    return notes.search_note(query=query, sort_by=sort_by)


def add_tags_by_title(*args):
    """
    Method that adds tags to a note by its title.
    :param args: Input parameters (title, tags).
    :return: String indicating successful addition of tags to a note.
    """
    if len(args) < 2:
        return "There is lack of parameters for 'add tags' command. " \
               "Check details with command 'help'."
    title = args[0]
    tags = list(args[1:])
    return notes.add_tags_by_title(title=title, tags=tags)


def change_note_title(*args):
    """
    Method that changes the title of a note.
    :param args: Input parameters (title, new_title).
    :return: String indicating successful title change of a note.
    """
    if len(args) < 2:
        return "There is lack of parameters for 'change note's title' " \
               "command. Check details with command 'help'."
    title = args[0]
    new_title = args[1]
    return notes.change_note_title(title=title, new_title=new_title)


def change_note_content(*args):
    """
    Method that changes the content of a note.
    :param args: Input parameters (title, new_content).
    :return: String indicating successful content change of a note.
    """
    if len(args) < 2:
        return "There is lack of parameters for 'change note's content' " \
               "command. Check details with command 'help'."
    title = args[0]
    new_content = " ".join(list(args[1:]))
    return notes.change_note_content(title=title, new_content=new_content)


def help_command() -> str:
    """
    Method that returns instructions for the bot commands.
    :return: String with instructions for the bot commands.
    TODO: rewrite method with all commands when they all will be implemented
    """
    return """List of supported commands:\n
           1 - 'hello' to greet the bot;\n
           2 - 'add' to add a contact, e.g. 'add John 380995057766';\n
           or 'add John 380995057766 30-05-1967';\n
           3 - 'change' to change an existing contact's phone,\n
           e.g. 'change John 380995051919 1234567890';\n
           4 - 'phone' to see a contact, e.g. 'phone John';\n
           5 - 'show all' to show all contacts which were add during the 
           session with the bot:\n
           6 - 'good bye', 'close' or 'exit' to stop the bot;\n
           7 - 'search na' or 'search 123' to search in the address book 
           by any match in name or phone;\n
           8 - 'delete john' to remove a whole contact by name.\n
           9 - 'help' to see description and supported commands.\n\n
           Each command, name or phone should be separated by a 
           space like ' '.
           Each command should be entered in order like 'command name 
           phone'.\n
           Each contact's name has to be unique.\n
           Each contact's name should be entered like a single word, if\n
           desired name is first name and last name, separate them with\n
           underscore, e.g. John_Wick.\n
           You can add only one phone to the name.\n
           Purpose of the bot to create, modify and save contacts during\n
           a single session. All data will be deleted after exit from the\n
           session."""


COMMANDS = {
    "help": help_command,
    "hello": hello,
    "add contact": add_contact,
    "delete contact": delete_contact,
    "change phone": change_phone,
    "change birthday": update_birthday,
    "phone": find_contact_phone,
    "show all contacts": show_all,
    "good bye": good_bye,
    "close": good_bye,
    "exit": good_bye,
    "show days to birthday": show_days_to_birthday,
    "search contact": search_contact,
    "add phone": add_phone,
    "add address": add_address,
    "add email": add_email,
    "upcoming birthdays": upcoming_birthdays,
    "add note": add_note,
    "delete note": delete_note,
    "show all notes": show_all_notes,
    "search note": search_note,
    "add tags": add_tags_by_title,
    "change note's title": change_note_title,
    "change note's content": change_note_content,
    "change email": change_email,
    "change address": change_address,
    "change name": change_name,
}


def main() -> None:
    """
    Method is responsible for creating an endless loop where all additional function is
    calling. The loop can be stopped by passing the appropriate commands (close, exit,
    good bye).
    :return: None.
    """
    while True:
        cli_input = prompt(message="Type a command>>> ",
                           completer=get_nested_completer(),
                           bottom_toolbar="Run 'help' command for getting additional "
                                          "information about bot commands")
        func_name, func, func_args = parse_cli_command(cli_input)
        print(func(*func_args))
        if func_name in ("good bye", "close", "exit"):
            break


if __name__ == "__main__":
    main()
