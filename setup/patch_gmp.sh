#!/usr/bin/env bash

#
#--------------------------------------------------------------------*/
#--- HerbGrind: a valgrind tool for Herbie              hg_main.c ---*/
#--------------------------------------------------------------------*/
#
#
# This file is part of HerbGrind, a valgrind tool for diagnosing
# floating point accuracy problems in binary programs and extracting
# problematic expressions.
#
# Copyright (C) 2016-2017 Alex Sanchez-Stern
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# 02111-1307, USA.
#
# The GNU General Public License is contained in the file COPYING.
#

# check to see if we should use GNU sed on homebrew
if hash gsed > /dev/null 2>&1 ; then
  SED="gsed"
else
  SED="sed"
fi

# Comment out uses of malloc, realloc, free, and fprinf, in the
# default memory functions for gmp. We'll be calling
# mp_set_memory_functions to override the default memory functions in
# our tool anyway, so the default ones wil never be called. But the
# linker will still try and link them, and since valgrind doesn't
# provide a standard c library to it's tools, it will fail, killing
# the build. So, we comment them out instead, and everything works
# fine.
$SED -i \
     -e 's/malloc.*(.*);/0;\/\/&/' \
     -e 's/realloc.*(.*);/0;\/\/&/' \
     -e 's/free.*(.*);/\/\/&/' \
     -e 's/fprintf.*(.*);/;\/\/&/'\
     -e 's/abort.*(.*);/;\/\/&/'\
     -e 's/raise.*(.*);/;\/\/&/'\
     ../deps/gmp-$1/invalid.c \
     ../deps/gmp-$1/memory.c \
     ../deps/gmp-$1/assert.c \
     ../deps/gmp-$1/errno.c \
     ../deps/gmp-$1/mpz/realloc.c
