#!/usr/bin/env python
# -*- coding: utf-8 -*-

cxxkw_text = '''
auto
break
case
char
const
continue
default
double
else
enum
extern
float
goto
inline
int
long
register
restrict
return
short
signed
sizeof
static
struct
switch
typedef
union
unsigned
void
volatile
while
_Bool
_Complex
_Imaginary
EXIT_FAILURE
EXIT_SUCCESS
size_t

bool
catch
class
const_cast
delete
dynamic_cast
explicit
export
false
friend
mutable
namespace
operator
private
protected
public
reinterpret_cast
static_cast
template
this
throw
true
typeid
typename
using
virtual
wchar_t

and_eq
bitand
bitor
compl
not_eq
or_eq
xor_eq

define
defined
elif
endif
error
ifdef
ifndef
include
pragma
undef

adjustfield
basefield
boolalpha
floatfield
internal
scientific
setbase
setiosflags
setprecision
showbase
showpoint
showpos
uppercase

exception
bad_alloc
bad_exception
bad_cast
bad_typeid
ios_base
failure
logic_error
domain_error
invalid_argument
length_error
out_of_range
runtime_error
range_error
overflow_error
underflow_error
uncaught_exception

__DATE__
__FILE__
__LINE__
__STDC__
__STDC_HOSTED__
__STDC_IEC_559__
__STDC_IEC_559_COMPLEX__
__STDC_ISO_10646__
__STDC_VERSION__
__TIME__
__func__
__cplusplus
__VA_ARGS__

__BORLANDC__
__CYGWIN__
__CYGWIN32__
__GNUC__
__WIN32__
__WINDOWS__

assert
ctype
errno
float
limits
locale
math
setjmp
signal
stdarg
stddef
stdio
stdlib
string
time

complex
fenv
inttypes
iso646
stdbool
stdint
tgmath
wchar
wctype

algorithm
bitset
complex
deque
exception
fstream
functional
iomanip
ios
iosfwd
iostream
istream
iterator
limits
list
locale

map
memory
new
numeric
ostream
queue
set
sstream
stack
stdexcept
streambuf
string
typeinfo
utility
valarray
vector

cassert
cctype
cerrno
cfloat
climits
clocale
cmath
csetjmp
csignal
cstdarg
cstddef
cstdio
cstdlib
cstring
ctime
'''

cxxkw_list = [kw.strip() for kw in cxxkw_text.splitlines() if kw]

def GetCxxKeywords():
    global cxxkw_list
    return cxxkw_list

def main(argv):
    global cxxkw_list
    for kw in GetCxxKeywords():
        assert kw

if __name__ == '__main__':
    import sys
    ret = main(sys.argv)
    if ret is None:
        ret = 0
    sys.exit(ret)