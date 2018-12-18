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
        # Strings
        if tag == 1:
            value = codecs.decode(value_bin,"utf-8")
            print("#{:5}: {:5} = {}" .format(counter, tag, value))
        # Ints
        elif tag == 3:
            value = int.from_bytes(value_bin, byteorder='big')
            print("#{:5}: {:5} = {}" .format(counter, tag, value))
        # Float
        elif tag == 4:
            value = float(value_bin, 16)
            print("#{:5}: {:5} = {}" .format(counter, tag, value))
        # Long
        elif tag == 5:
            value = long(value_bin, 16)
            print("#{:5}: {:5} = {}" .format(counter, tag, value))
            counter+=1
        # Double
        elif tag == 6:
            value = float(value_bin, 16)
            print("#{:5}: {:5} = {}" .format(counter, tag, value))
            counter+=1
        # Index
        elif tag == 7:
            print_class_info(jc, counter, value_bin)
        elif tag == 8:
            print_string_info(jc, counter, value_bin)
        # Index pair
        elif tag in [9, 10, 11, 12]:
            value1 = int.from_bytes(value_bin, byteorder='big')
            value_bin2 = jc.read(2)
            value2 = int.from_bytes(value_bin2, byteorder='big')
            value = (value1, value2)
            print("#{:5}: {:5} = [{} : {}]" .format(counter, tag, value1, value2))
        elif tag == 15:
            value1 = int.from_bytes(value_bin, byteorder='big')
            value_bin2 = jc.read(2)
            value2 = int.from_bytes(value_bin2, byteorder='big')
            value = (value1, value2)
            print("#{:5}: {:5} = [{} -> {}]" .format(counter, tag, method_handel_tags[value1], value2))
        # Exit if you encounter an unknown tag
        else:
            print("ERROR!\nUnknown tag {} at index {}!" .format(tag, counter))
            sys.exit(1)
        constant_pool.append(value)

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

# Constant pool descriptors
def print_class_info(jc, counter, value_bin):
    """
    Print constant class (or interface) information.

    Data structure:
    U1: tag = 7
    U2: name_index - Contains index in the CP which contains an UTF-8 encoded
        name of a class or interface.
    """
    tag = 7
    value = int.from_bytes(value_bin, byteorder='big')
    print("#{:5}: {:5} = {}" .format(counter, tag, value))

def print_string_info(jc, counter, value_bin):
    """
    Tag(8): Print constant String information.

    Data structure:
    U1: tag = 8
    U2: string_index - Index of CP containing UTF-8 string.
    """
    tag = 8
    value = int.from_bytes(value_bin, byteorder='big')
    print("#{:5}: {:5} = {}" .format(counter, tag, value))

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
