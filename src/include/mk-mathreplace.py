#!/usr/bin/env python

#--------------------------------------------------------------------#
#--- HerbGrind: a valgrind tool for Herbie      mk_mathreplace.py ---#
#--------------------------------------------------------------------#


   # This file is part of HerbGrind, a valgrind tool for diagnosing
   # floating point accuracy problems in binary programs and extracting
   # problematic expressions.

   # Copyright (C) 2016-2017 Alex Sanchez-Stern

   # This program is free software; you can redistribute it and/or
   # modify it under the terms of the GNU General Public License as
   # published by the Free Software Foundation; either version 3 of the
   # License, or (at your option) any later version.

   # This program is distributed in the hope that it will be useful, but
   # WITHOUT ANY WARRANTY; without even the implied warranty of
   # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
   # General Public License for more details.

   # You should have received a copy of the GNU General Public License
   # along with this program; if not, write to the Free Software
   # Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
   # 02111-1307, USA.

   # The GNU General Public License is contained in the file COPYING.


class Op(object):
    def __init__(self, func, plain_name, nargs, mpfr_func=None, needsround=True, precision=64, native_func=None):
        self.func = func
        self.nargs = nargs
        self.plain_name = plain_name
        self.needsround = needsround
        self.precision = precision
        if (mpfr_func == None):
            self.mpfr_func = "mpfr_{}".format(func)
        else:
            self.mpfr_func = mpfr_func
        self.native_func = native_func

def write_mathreplace_funcs(ops, fname):
    with open(fname, "w") as f:
        f.write("#ifndef _MATHREPLACE_FUNCS_H\n")
        f.write("#define _MATHREPLACE_FUNCS_H\n")
        f.write("\n")
        f.write("// This monstrosity of a file sets up a lot of the machinery to\n")
        f.write("// replace libm functions called by client programs with a call into\n")
        f.write("// tool code which handles them properly. Basically, I wanted to make\n")
        f.write("// it very easy to add new libm functions without having to change\n")
        f.write("// code in like four different places. So I took every place you would\n")
        f.write("// have to change code to add new functions, and abstraced them away\n")
        f.write("// into macros, which all live in this file. This means the rest of\n")
        f.write("// the project is agnostic to which functions from libm we support,\n")
        f.write("// but it also means there are mysterious macros scattered throughout\n")
        f.write("// that code, and this file is a giant mess. Luckily, you should never\n")
        f.write("// actually touch it yourself, because it's instead generated by the\n")
        f.write("// mk_mathreplace.py python script.\n")
        f.write("\n")
        f.write("// These operations are based on the ones that Herbie supports natively.\n")
        f.write("\n")

        f.write("// A list of all the unary operations, for the enum definition farther\n")
        f.write("// down in the file.\n")
        f.write("#define UNARY_OPS_LIST \\\n")
        for op in ops:
            if (op.nargs == 1):
                f.write("  OP_{}, \\\n".format(op.func.upper()))
        f.write("\n")

        f.write("// A list of all the binary ops comma seperated, for the enum\n")
        f.write("// definition farther down in the file.\n")
        f.write("#define BINARY_OPS_LIST \\\n")
        for op in ops:
            if (op.nargs == 2):
                f.write("  OP_{}, \\\n".format(op.func.upper()))
        f.write("\n")

        f.write("// A list of all the ternary ops comma seperated, for the enum\n")
        f.write("// definition farther down in the file.\n")
        f.write("#define TERNARY_OPS_LIST \\\n")
        for op in ops:
            if (op.nargs == 3):
                f.write("   OP_{}, \\\n".format(op.func.upper()))
        f.write("\n")

        f.write("// A bunch of case statements for each unary op whose mpfr function\n"
                "// doesn't need a rounding mode, used in runtime/hg_mathreplace.c\n")
        f.write("// The formatting of the following might seem a little weird,\n"
                "// but we leave off the first \"case\" and the last \":\"\n"
                "// because it makes it easier to use the macro on the clientside.\n");
        f.write("#define UNARY_OPS_ROUND_CASES \\\n")
        u_ops_round = [op for op in ops
                       if op.nargs == 1 and op.needsround]
        write_labels(f, u_ops_round)

        f.write("// Same as above, but for those that don't need a rounding mode.\n")
        f.write("#define UNARY_OPS_NOROUND_CASES \\\n")
        u_ops_noround = [op for op in ops
                         if op.nargs == 1 and not op.needsround]
        write_labels(f, u_ops_noround)

        f.write("// For places where we don't care about the rounding mode.\n")
        f.write("#define UNARY_OPS_CASES                         \\\n")
        f.write("       UNARY_OPS_ROUND_CASES:                     \\\n")
        f.write("  case UNARY_OPS_NOROUND_CASES\n")
        f.write("\n")

        f.write("// The binary operation cases, used in runtime/hg_mathreplace.c\n")
        f.write("#define BINARY_OPS_CASES \\\n")
        b_ops = [op for op in ops
                 if op.nargs == 2]
        write_labels(f, b_ops)

        f.write("// The ternary operation cases, used in runtime/hg_mathreplace.c\n")
        f.write("#define TERNARY_OPS_CASES \\\n")
        t_ops = [op for op in ops
                 if op.nargs == 3]
        write_labels(f, t_ops)

        f.write("// The single precision cases\n")
        f.write("#define SINGLE_CASES \\\n")
        single_ops = [op for op in ops
                      if op.precision == 32]
        write_labels(f, single_ops)

        f.write("// The double precision cases\n")
        f.write("#define DOUBLE_CASES \\\n")
        double_ops = [op for op in ops
                      if op.precision == 64]
        write_labels(f, double_ops)

        f.write("// A switch statement to get the mpfr function for each op.\n")
        f.write("#define GET_UNARY_OPS_ROUND_F(fvar, op) \\\n")
        write_switch_funcs(f, u_ops_round)

        f.write("// Same as above, but for those that don't need a rounding mode.\n")
        f.write("#define GET_UNARY_OPS_NOROUND_F(fvar, op) \\\n")
        write_switch_funcs(f, u_ops_noround)

        f.write("// Same as above, but binary ops\n")
        f.write("#define GET_BINARY_OPS_F(fvar, op) \\\n")
        write_switch_funcs(f, b_ops)

        f.write("// Same as above, but ternary ops\n")
        f.write("#define GET_TERNARY_OPS_F(fvar, op) \\\n")
        write_switch_funcs(f, t_ops)

        f.write("// Getting a string name of the op.\n")
        f.write("#define GET_OP_NAMES(namevar, op)\\\n")
        write_switch_names(f, ops)

        f.write("// Running the libm version of the op.\n")
        f.write("#define RUN(result, op, args) \\\n")
        write_switch_run(f, ops)

        f.write("// Call the wrapping macro, defined at the call site in hg_mathwrap.c,\n")
        f.write("// to wrap each function we support.\n")
        f.write("#define WRAP_UNARY_OPS \\\n")
        for op in ops:
            if (op.nargs == 1):
                f.write("  WRAP_UNARY({}, OP_{}); \\\n".format(op.func, op.func.upper()))
        f.write("\n")

        f.write("// Same for binary ops.\n")
        f.write("#define WRAP_BINARY_OPS \\\n")
        for op in ops:
            if (op.nargs == 2):
                f.write("  WRAP_BINARY({}, OP_{}); \\\n".format(op.func, op.func.upper()))
        f.write("\n")

        f.write("// Same for binary ops.\n")
        f.write("#define WRAP_TERNARY_OPS \\\n")
        for op in ops:
            if (op.nargs == 3):
                f.write("  WRAP_TERNARY({}, OP_{}); \\\n".format(op.func, op.func.upper()))
        f.write("\n")

        f.write("// Finally, define an enum for the operations we support.\n")
        f.write("typedef enum {\n")
        f.write("  OP_INVALID,\n");
        f.write("  // Unary functions\n")
        f.write("  UNARY_OPS_LIST\n")
        f.write("  // Binary\n")
        f.write("  BINARY_OPS_LIST\n")
        f.write("  // Ternary\n")
        f.write("  TERNARY_OPS_LIST\n")
        f.write("} OpType;\n")
        f.write("\n")

        f.write("#endif\n")

ops = []

def addOp(name, plain_name, nargs,
          hasfloat=True, needsRound=True,
          mpfr_func=None, native_func=None):
    mpfr_fn = "mpfr_" + name
    if (mpfr_func != None):
        mpfr_fn = mpfr_func
    if native_func == None:
        native_func = name

    ops.append(Op(name, plain_name, nargs,
                  mpfr_func=mpfr_fn,
                  needsround=needsRound,
                  native_func=native_func))
    ops.append(Op("ZuZu"+name, plain_name, nargs,
                  mpfr_func=mpfr_fn,
                  needsround=needsRound,
                  native_func=native_func))
    ops.append(Op("ZuZu"+name+"Zuavx", plain_name, nargs,
                  mpfr_func=mpfr_fn,
                  needsround=needsRound,
                  native_func=native_func))
    ops.append(Op("ZuZu"+name+"Zufma4", plain_name, nargs,
                  mpfr_func=mpfr_fn,
                  needsround=needsRound,
                  native_func=native_func))
    ops.append(Op("ZuZuieee754Zu"+name, plain_name, nargs,
                  mpfr_func=mpfr_fn,
                  needsround=needsRound,
                  native_func=native_func))
    ops.append(Op("ZuZuieee754Zu"+name+"Zuavx", plain_name, nargs,
                  mpfr_func=mpfr_fn,
                  needsround=needsRound,
                  native_func=native_func))
    ops.append(Op("ZuZuieee754Zu"+name+"Zusse2", plain_name, nargs,
                  mpfr_func=mpfr_fn,
                  needsround=needsRound,
                  native_func=native_func))
    ops.append(Op("ZuZuieee754Zu"+name+"Zufma4", plain_name, nargs,
                  mpfr_func=mpfr_fn,
                  needsround=needsRound,
                  native_func=native_func))

    if hasfloat:
        if (native_func != None):
            native_fn_f = native_func + "f"
        else:
            native_fn_f = None
        ops.append(Op(name + "f",
                      plain_name + " (float)",
                      nargs,
                      mpfr_func=mpfr_fn,
                      needsround=needsRound,
                      precision=32,
                      native_func=native_fn_f))

def write_labels(f, l):
    for i, op in enumerate(l):
        if i == 0:
            f.write("       OP_{}: \\\n".format(op.func.upper()))
        elif i != len(l) - 1:
            f.write("  case OP_{}: \\\n".format(op.func.upper()))
        else:
            f.write("  case OP_{}".format(op.func.upper()))
    f.write("\n")

def write_switch_run(f, l):
    f.write("  switch(op){ \\\n")
    for op in l:
        f.write("  case OP_{}: \\\n".format(op.func.upper()))
        if op.nargs == 1:
            f.write("    result = {}(args[0]); \\\n".format(op.native_func))
        elif op.nargs == 2:
            f.write("    result = {}(args[0], args[1]); \\\n".format(op.native_func))
        elif op.nargs == 3:
            f.write("    result = {}(args[0], args[1], args[2]); \\\n".format(op.native_func))
        f.write("    break; \\\n");
    f.write("  default: \\\n")
    f.write("    result = 0.0; \\\n")
    f.write("    break; \\\n")
    f.write("  }\n")
    f.write("\n");

def write_switch_funcs(f, l):
    f.write("  switch(op){ \\\n")
    for op in l:
        f.write("  case OP_{}: \\\n".format(op.func.upper()))
        f.write("    fvar = {}; \\\n".format(op.mpfr_func))
        f.write("    break; \\\n")
    f.write("  default: \\\n")
    f.write("    break; \\\n")
    f.write("  }\n")
    f.write("\n")

def write_switch_names(f, l):
    f.write("  switch(op){ \\\n")
    f.write("  case OP_INVALID: \\\n")
    f.write("    namevar = \"invalid\"; \\\n")
    f.write("    break;\\\n")
    for op in l:
        f.write("  case OP_{}: \\\n".format(op.func.upper()))
        f.write("    namevar = \"{}\"; \\\n".format(op.native_func))
        f.write("    break;\\\n")
    f.write("  default: \\\n"
            "    break; \\\n"
            "  }\n"
            "\n")

addOp("sqrt", "square root", 1)
addOp("cbrt", "cube root", 1)

addOp("fabs", "absolute value", 1, mpfr_func="mpfr_abs")
addOp("logb", "get exponent", 1)
addOp("rint", "round to nearest integer", 1)

addOp("ceil", "ceiling", 1, needsRound=False)
addOp("floor", "floor", 1, needsRound=False)
addOp("round", "round", 1, needsRound=False)
addOp("trunc", "truncate", 1, needsRound=False)

addOp("exp", "exponentiate", 1)
addOp("ZuZuexp1", "exponentiate", 1,
      mpfr_func="mpfr_exp", native_func="exp")

addOp("exp2", "base-two exponentiate", 1)
addOp("expm1", "exponentiate minus one", 1)

addOp("log", "log", 1)
addOp("ZuZulogZufinite", "log", 1,
      mpfr_func="mpfr_log", native_func="log")

addOp("log10", "log base ten", 1)
addOp("ZuZulog10Zufinite", "log", 1,
      mpfr_func="mpfr_log10", native_func="log10")

addOp("log1p", "plus one log", 1)
addOp("log2", "log base two", 1)

addOp("erf", "error function", 1)
addOp("erfc", "complementary error function", 1)
addOp("lgamma", "log gamma function", 1, mpfr_func="mpfr_lgamma2")
addOp("tgamma", "gamma function", 1, mpfr_func="mpfr_gamma")
addOp("j0", "order zero first kind bessel function", 1)
addOp("j1", "order one first kind bessel function", 1)
addOp("y0", "order zero second kind bessel function", 1)
addOp("y1", "order one second kind bessel function", 1)

addOp("cos", "cosine", 1)
addOp("sin", "sine", 1)
addOp("tan", "tangent", 1)
addOp("asin", "arc sine", 1)
addOp("acos", "arc cosine", 1)
addOp("atan", "arc tangent", 1)

addOp("sinh", "hyperbolic sine", 1)
addOp("cosh", "hyperbolic cosine", 1)
addOp("tanh", "hyperbolic tangent", 1)
addOp("asinh", "hyperbolic arc sine", 1)
addOp("acosh", "hyperbolic arc cosine", 1)
addOp("atanh", "hyperbolic arc tangent", 1)

addOp("atan2", "arc tangent (two arguments)", 2)
addOp("hypot", "hypotenuse", 2)

addOp("pow", "power", 2)
addOp("ZuZupowZufinite", "power", 2,
      mpfr_func="mpfr_pow", native_func="pow")
addOp("slowpow", "power", 2,
      mpfr_func="mpfr_pow", native_func="pow")
addOp("fmod", "modulus", 2)
addOp("copysign", "copy sign", 2)
addOp("fdim", "positive difference", 2, mpfr_func="mpfr_dim")
addOp("fmax", "maximum", 2, mpfr_func="mpfr_max")
addOp("fmin", "minimum", 2, mpfr_func="mpfr_min")
addOp("remainder", "remainder", 2)

addOp("fma", "fused multiply-add", 3)

write_mathreplace_funcs(ops, "mathreplace-funcs.h")
