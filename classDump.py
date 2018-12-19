#!/usr/bin/python3
################################################################################
#                                                                              #
#                                 {o,o}                                        #
#                                 |)__)                                        #
#                                 -"-"-                                        #
#                                                                              #
################################################################################
#
# Java classfile dumper.
# Pass filepath as the first argument:
# ./classDump.py <class_file>
#
##################################---IMPORTS---#################################

import sys
import binascii
import codecs
import os

################################################################################

################################---VARIABLES---#################################

# Check if specified file exists
if os.path.isfile(sys.argv[1]):
# Open the file in binary mode.
    jc = open(sys.argv[1], 'rb')
else:
    #Exit if file doesn't exist
    print("ERROR!\n Given Classfile does not exist: {}" . format(sys.argv[1]))
    sys.exit(1)


# Constatnt pool types with size.
# If complex data types are present only initial read size is specified.
tags = {
    1:("UTF-8", 2),
    3:("Integer", 4),
    4:("Float", 4),
    5:("Long", 8),
    6:("Double", 8),
    7:("Class", 2),
    8:("String", 2),
    9:("Fieldref", 2),
    10:("Methodref", 2),
    11:("InterfaceMethodref", 2),
    12:("NameAndType", 2),
    15:("MethodHandle", 1),
    16:("MethodType", 2),
    18:("InvokeDynamic", 4) }

# Method handle tags
method_handel_tags = {
    1:"get_field",
    2:"get_static",
    3:"get_field",
    4:"put_static",
    5:"invoke_virtual",
    6:"invoke_static",
    7:"invoke_special",
    8:"new_invoke_special",
    9:"invoke_interface" }

# Empty constant pool
constant_pool=[]

################################################################################

################################---METHODS---###################################

def print_cp_info(jc, constant_pool_count):
    """
    Work trough the constant pool, and pretty print it.
    """

    for counter in range(1,constant_pool_count):
        # First we reed the 1 byte of that tag info to get the type
        tag = int.from_bytes(jc.read(1), byteorder='big')
        # With the type known we get the value length
        if tag > 1:
            read_bytes = tags[tag][1]
        else:
            # Which in case of the UTF-8 type is written in the first 2 bytes
            read_bytes = int.from_bytes(jc.read(2), byteorder='big')

        value_bin = jc.read(read_bytes)
        if tag == 1:
            print_utf8_info(counter, value_bin)
        elif tag == 3:
            print_integer_info(counter, value_bin)
        elif tag == 4:
            print_float_info(counter, value_bin)
        elif tag == 5:
            print_long_info(counter, value_bin)
            counter+=1
        elif tag == 6:
            print_double_info(counter, value_bin)
            counter+=1
        elif tag == 7:
            print_class_info(counter, value_bin)
        elif tag == 8:
            print_string_info(counter, value_bin)
        elif tag == 9:
            print_field_ref_info(counter, value_bin)
        elif tag == 10:
            print_method_ref_info(counter, value_bin)
        elif tag == 11:
            print_interface_method_ref_info(counter, value_bin)
        elif tag == 12:
            print_name_and_type_info(counter, value_bin)
        elif tag == 15:
            print_method_handle_info(counter, value_bin)
        elif tag == 16:
            print_method_type_info(counter, value_bin)
        elif tag == 18:
            print_invoke_dynamic_info(counter, value_bin)
        else:
            print("ERROR!\nUnknown tag {} at index {}!" .format(tag, counter))
            sys.exit(1)

# Constant pool descriptors

def print_utf8_info(counter, value_bin):
    """
     CONSTANT_Utf8_info: Print UTF-String

     Data structure:
     U1: tag = 1
     U2: length
     U1: bytes[Length] - UTF-8 encoded characters
    """
    tag = 1
    value = codecs.decode(value_bin,"utf-8")
    print("#{:5}: {:5} = {}" .format(counter, tag, value))
    constant_pool.append(value)

def print_integer_info(counter, value_bin):
    """
    CONSTANT_Integer_info: Print integer

    Data structure:
    U1: tag = 3
    U4: bytes = Value of the Int constant
    Uses same structure as CONSTANT_Integer_info
    """
    tag = 3
    value = int.from_bytes(value_bin, byteorder='big')
    print("#{:5}: {:5} = {}" .format(counter, tag, value))
    constant_pool.append(value)

def print_float_info(counter, value_bin):
    """
    CONSTANT_Float_info: Print float

    Data structure:
    U1: tag = 4
    U4: bytes = Value of the Float constant
    Uses same structure as CONSTANT_Integer_info
    """
    tag = 4
    value = float(value_bin, 16)
    print("#{:5}: {:5} = {}" .format(counter, tag, value))
    constant_pool.append(value)

def print_long_info(counter, value_bin):
    """
    CONSTANT_Long_info: Print float

    Data structure:
    U1: tag = 5
    U4: high_bytes
    U4: low_bytes
    ---
    Note: Takes 2 entries in the constant pool table - so we must skip 1 couter.
    As noted in official documentation: 'In retrospect, making 8-byte constants
        take two constant pool entries was a poor choice.'
    """
    tag = 5
    value = long(value_bin, 16)
    print("#{:5}: {:5} = {}" .format(counter, tag, value))
    counter+=1
    return (value, counter)
    constant_pool.append(value)

def print_double_info(counter, value_bin):
    """
    CONSTANT_Double_info: Print double

    Data structure:
    U1: tag = 6
    U4: high_bytes
    U4: low_bytes
    ---
    Note: Takes 2 entries in the constant pool table - so we must skip 1 couter.
    As noted in official documentation: 'In retrospect, making 8-byte constants
        take two constant pool entries was a poor choice.'
    """
    tag = 6
    value = float(value_bin, 16)
    print("#{:5}: {:5} = {}" .format(counter, tag, value))
    counter+=1
    constant_pool.append(value)

def print_class_info(counter, value_bin):
    """
    CONSTANT_Class_info: Print constant class (or interface) information.

    Data structure:
    U1: tag = 7
    U2: name_index - Contains index in the CP which contains an UTF-8 encoded
        name of a class or interface.
    """
    tag = 7
    value = int.from_bytes(value_bin, byteorder='big')
    print("#{:5}: {:5} = {}" .format(counter, tag, value))
    constant_pool.append(value)

def print_string_info(counter, value_bin):
    """
    CONSTANT_String_info: Print constant String information.

    Data structure:
    U1: tag = 8
    U2: string_index - Index of CP containing UTF-8 string.
    """
    tag = 8
    value = int.from_bytes(value_bin, byteorder='big')
    print("#{:5}: {:5} = {}" .format(counter, tag, value))
    constant_pool.append(value)

def print_field_ref_info(counter, value_bin):
    """
    CONSTANT_Fieldref_info: Print Field information.

    Data structure:
    U1: tag = 9
    U2: class_index - valid index in the CP. Must point to an Class type.
    U2: name_and_type_index - calid index in the CP
    Same data structure as
    """
    tag         = 9
    value1      = int.from_bytes(value_bin, byteorder='big')
    value_bin2  = jc.read(2)
    value2      = int.from_bytes(value_bin2, byteorder='big')
    print("#{:5}: {:5} = [{} : {}]" .format(counter, tag, value1, value2))
    constant_pool.append((value1, value2))

def print_method_ref_info(counter, value_bin):
    """
    CONSTANT_Methodref_info: Print Method information.

    Data structure:
    U1: tag = 10
    U2: class_index - valid index in the CP - Must point to an interface type.
    U2: name_and_type_index
    """
    tag         = 10
    value1      = int.from_bytes(value_bin, byteorder='big')
    value_bin2  = jc.read(2)
    value2      = int.from_bytes(value_bin2, byteorder='big')
    print("#{:5}: {:5} = [{} : {}]" .format(counter, tag, value1, value2))
    constant_pool.append((value1, value2))

def print_interface_method_ref_info(counter, value_bin):
    """
    CONSTANT_InterfaceMethodref_info: Print Interface method information.

    Data structure:
    U1: tag = 11
    U2: class_index - valid index in the CP - Can point to either class or
        interface type
    U2: name_and_type_index
    """
    tag         = 11
    value1      = int.from_bytes(value_bin, byteorder='big')
    value_bin2  = jc.read(2)
    value2      = int.from_bytes(value_bin2, byteorder='big')
    print("#{:5}: {:5} = [{} : {}]" .format(counter, tag, value1, value2))
    constant_pool.append((value1, value2))

def print_name_and_type_info(counter, value_bin):
    """
    CONSTANT_NameAndType_info: Print Name and type information.

    Data structure:
    U1: tag = 12
    U2: name_index - valid CP index.
    U2: descriptor_index - valid CP index.
    """
    tag         = 12
    value1      = int.from_bytes(value_bin, byteorder='big')
    value_bin2  = jc.read(2)
    value2      = int.from_bytes(value_bin2, byteorder='big')
    print("#{:5}: {:5} = [{} : {}]" .format(counter, tag, value1, value2))
    constant_pool.append((value1, value2))

def print_method_handle_info(counter, value_bin):
    """
    CONSTANT_MethodHandle_info: Prints Method handle information.

    Data structure:
    U1: tag = 15
    U1: reference_kind - values 1-9
    U2: reference_index - Index of the CP table.
    ---
    Based on the reference_kind, Reference index must point to a certain type:
    - reference_kind (1,2,3,4) -> CONSTANT_Fieldref_info
    - reference_kind (5,6,7,8) -> CONSTANT_Methodref_info
    - reference_kind (9) -> CONSTANT_InterfaceMethodref_info
    """
    tag = 15
    value1 = int.from_bytes(value_bin, byteorder='big')
    value_bin2 = jc.read(2)
    value2 = int.from_bytes(value_bin2, byteorder='big')
    print("#{:5}: {:5} = [{} -> {}]" .format(counter, tag, method_handel_tags[value1], value2))
    constant_pool.append((value1, value2))

def print_method_type_info(counter, value_bin):
    """
    CONSTANT_MethodType_info: Print Method type info.

    Data structure:
    U1: tag = 16
    U2: descriptor_index: CP table index -> Points to a method descriptor.
    """
    tag =  16
    value = int.from_bytes(value_bin, byteorder='big')
    print("#{:5}: {:5} = {}" .format(counter, tag, value))
    constant_pool.append(value)

def print_invoke_dynamic_info(counter, value_bin):
    """
     CONSTANT_InvokeDynamic_info: Describes the invokedynamic instruction.

     Data structure:
     U1: tag = 18
     U2: bootstrap_method_attr_index - index in the bootstrap_methods
     U2: name_and_type_index valid index of the CP table.
    """
    tag = 18
    value1 = int.from_bytes(value_bin, byteorder='big')
    value_bin2 = jc.read(2)
    value2 = int.from_bytes(value_bin2, byteorder='big')
    print("#{:5}: {:5} = [{} -> {}]" .format(counter, tag, method_handel_tags[value1], value2))
    constant_pool.append((value1, value2))

def print_interfaces(jc, interfaces_count):
    """
    Print all interfaces.

    Each interface has:
    u1 - tag which is of type Class
    u2 - index pointing at the object in constant pool table
    """
    for counter in range(0, interfaces_count):
        tag = int.from_bytes(jc.read(1), byteorder='big')
        index = int.from_bytes(jc.read(2), byteorder='big')
        print("#{:5}: {5}" .format(tags[tag][0], index))

def print_fields (jc, fields_count):
        """
        Print all fields.

        Each field has:
        u2 - access flags
        u2 - named index
        u2 - descriptor Index
        u2 - attributes count
        [attributes_count] attributes_info

        Access flags are:
        0x0001 - public
        0x0002 - private
        0x0004 - protected
        0x0008 - static
        0x0010 - final
        0x0040 - volatile
        0x0080 - transient
        0x1000 - synthetic
        0x4000 - enum
        """
        for counter in range(0, fields_count):
            access_flags = codecs.decode(binascii.hexlify(jc.read(2)))
            named_index = int.from_bytes(jc.read(2), byteorder='big')
            descriptor_index = int.from_bytes(jc.read(2), byteorder='big')
            attributes_count = int.from_bytes(jc.read(2), byteorder='big')
            if attributes_count:
                print(" > Attributes:")
                print_attributes(jc, attributes_count)
                print(" > ---\n")
            print("{} | [{}, {}] ( {} ):" .format(access_flags, named_index, descriptor_index, attributes_count))

def print_methods(jc, methods_count):
    """
    Print all methods

    u2 - access flags
    u2 - named index
    u2 - descriptor index
    u2 - attributes count
    [attributes_count] attributes_info

    Access flags:
    0x0001 - PUBLIC
    0x0002 - PRIVATE
    0x0004 - PROTECTED
    0x0008 - STATIC
    0x0010 - FINAL
    0x0020 - SYNCHRONIZED
    0x0040 - BRIDGE
    0x0080 - VARARGS
    0x0100 - NATIVE
    0x0400 - ABSTRACT
    0x0800 - STRICT
    0x1000 - SYNTHETIC
    """
    for counter in range(0, methods_count):
        access_flags = codecs.decode(binascii.hexlify(jc.read(2)))
        named_index = int.from_bytes(jc.read(2), byteorder='big')
        descriptor_index = int.from_bytes(jc.read(2), byteorder='big')
        attributes_count = int.from_bytes(jc.read(2), byteorder='big')
        if attributes_count:
            print(" > Attributes:")
            print_attributes(jc, attributes_count)
            print(" > ---\n")

        print("{} | [{}, {}] ( {} ):" .format(access_flags, named_index, descriptor_index, attributes_count))

def print_exception_table(jc, exception_table_length):
    """
    Print exception table

    Each exception has 4 values
    - start_pc from which point in code an exception is active
    - end_pc to which point in code, an exception is valid
    - handler_pc -start of the exception handle
    - catch_type - exception type.
    All 4 are constant_pool index values.
    """

    print("Exception table({})[start_pc, end_pc, handler_pc, catch_type]:" .format(exception_table_length))

    for jc_exception in range(0, exception_table_length):
        start_pc = int.from_bytes(jc.read(2), byteorder='big')
        end_pc = int.from_bytes(jc.read(2), byteorder='big')
        handler_pc = int.from_bytes(jc.read(2), byteorder='big')
        catch_type = int.from_bytes(jc.read(2), byteorder='big')
        print("-> {} | {} | {} | {}" .format(start_pc, end_pc, handler_pc, catch_type))
    print

def print_attributes(jc, attributes_count):
    """
    Attributes list

    u2 - Attribute name index
    u4 - attribute length
    u1 - info[attribute length]
    """
    for a_count in range(0, attributes_count):
        attribute_name_index = int.from_bytes(jc.read(2), byteorder='big')
        attribute_lenght = int.from_bytes(jc.read(4), byteorder='big')
        value = int.from_bytes(jc.read(attribute_lenght), byteorder='big')
        print(" - {} ( {} )" .format(attribute_name_index, attribute_lenght))

################################################################################

##################################---RUN---#####################################

print("\nDecoding java class file: {}\n" . format(sys.argv[1]))
print("################################################################################\n")
# Magic - 4 bytes
# First 4 Bytes also known as Magic number, spell "CAFE BABE".
# We use binascii.hexlify and codecs.decode to decode from hex to UTF-8 string
print("Magic: {} {}" .format(codecs.decode(binascii.hexlify(jc.read(2)), "UTF-8"), codecs.decode(binascii.hexlify(jc.read(2)), "UTF-8")))

# Minor version - [2 bytes] + Major version - [2 bytes]
# Since Minor version is in the file first, we need to swap them.
# We use base 16 for integer conversion
print("Version: {1}.{0}" .format(int.from_bytes(jc.read(2), byteorder='big'), int.from_bytes(jc.read(2), byteorder='big')))

# Constant_pool_count - [2 bytes]
constant_pool_count = int.from_bytes(jc.read(2), byteorder='big')
print("Constant_pool_count: {}" .format(constant_pool_count))

# cp_info - [constant_pool_count - 1]
# cp_info contains 1 less item than constant_pool_count state - makes for loops easier.
print("cp_info:\n---")

print_cp_info(jc, constant_pool_count)

print("---")

# Access flags - [2 bytes]
# A set of flags as follows:
# 0x0001 - PUBLIC
# 0x0010 - FINAL
# 0x0020 - SUPER
# 0x0200 - INTERFACE
# 0x0400 - ABSTRACT
# 0x1000 - SYNTHETIC
# 0x2000 - ANNOTATION
# 0x4000 - ENUM

access_flags = codecs.decode(binascii.hexlify(jc.read(2)))
print("Access flags: {}" .format(access_flags))

# This class - [2 bytes]
this_class = int.from_bytes(jc.read(2), byteorder='big')
print("This_class: {}" .format(this_class))

# Superclass - [2 bytes]
superclass = int.from_bytes(jc.read(2), byteorder='big')
print("Superclass: {}" .format(superclass))

# Interface count - [2 bytes]
interface_count = int.from_bytes(jc.read(2), byteorder='big')
print("Interface count: {}" .format(interface_count))

# Interfaces list
print("Interfaces:")
if interface_count:
    print_interfaces(jc, interface_count)
print("---\n")

# Fields count - [2 bytes]
fields_count = int.from_bytes(jc.read(2), byteorder='big')
print("Fields count: {}" .format(fields_count))

# Fields list
print("Fields:")
if fields_count:
    print_fields(jc, fields_count)
print("---\n")

# Methods count - [2 bytes]
methods_count = int.from_bytes(jc.read(2), byteorder='big')
print("Methods count: {}" .format(methods_count))

# Methods
print("Methods:")
if methods_count:
    print_methods(jc, methods_count)
print("---\n")

# Attributes count - [2 bytes]
attributes_count = int.from_bytes(jc.read(2), byteorder='big')
print("Attributes count: {}" .format(attributes_count))

# Attributes
print("Attributes:")
if attributes_count:
    print_attributes(jc, attributes_count)
print("---\n")

# Closing file
jc.close()

################################################################################
