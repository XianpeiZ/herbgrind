/*--------------------------------------------------------------------*/
/*--- Herbgrind: a valgrind tool for Herbie                marks.h ---*/
/*--------------------------------------------------------------------*/

/*
   This file is part of Herbgrind, a valgrind tool for diagnosing
   floating point accuracy problems in binary programs and extracting
   problematic expressions.

   Copyright (C) 2016-2017 Alex Sanchez-Stern

   This program is free software; you can redistribute it and/or
   modify it under the terms of the GNU General Public License as
   published by the Free Software Foundation; either version 3 of the
   License, or (at your option) any later version.

   This program is distributed in the hope that it will be useful, but
   WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
   General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program; if not, write to the Free Software
   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
   02111-1307, USA.

   The GNU General Public License is contained in the file COPYING.
*/
#ifndef _MARKS_H
#define _MARKS_H

#include "pub_tool_basics.h"
#include "../../helper/list.h"

#include "shadowop-info.h"
#include "../value-shadowstate/value-shadowstate.h"
#include "../value-shadowstate/shadowval.h"

typedef struct _markInfo {
  Addr addr;
  const char* markType;
  InfluenceList influences;
  ErrorAggregate eagg;
  SymbExpr* expr;
} MarkInfo;

typedef struct _markInfoArray {
  // So we can store it in a hash table easily.
  struct _markInfoArray* next;
  Addr addr;
  int nmarks;
  MarkInfo* marks;
} MarkInfoArray;

typedef struct _intMarkInfo {
  struct _intMarkInfo* next;

  Addr addr;
  const char* markType;
  InfluenceList influences;
  long int num_hits;
  long int num_mismatches;
  int nargs;
  SymbExpr** exprs;
} IntMarkInfo;

void maybeMarkImportant(ShadowValue* val, double clientVal, int argIdx, int nargs);
void maybeMarkImportantAtAddr(ShadowValue* val, double clientValue, int argIdx, int nargs,
                              Addr callAddr);
void markImportant(ShadowValue* val, double clientVal, int argIdx, int nargs);
void markEscapeFromFloat(const char* markType,
                         int mismatch,
                         int numVals, ShadowValue** values);
IntMarkInfo* getIntMarkInfo(Addr callAddr, const char* markType);
MarkInfo* getMarkInfo(Addr callAddr, int argIdx, int nargs);
void printMarkInfo(MarkInfo* info);
int isSubexpr(SymbExpr* needle, SymbExpr* haystack, int depth);
InfluenceList filterInfluenceSubexprs(InfluenceList influences);
InfluenceList filterUnimprovableInfluences(InfluenceList influences);

#endif
