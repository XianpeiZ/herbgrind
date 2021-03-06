/*--------------------------------------------------------------------*/
/*--- Herbgrind: a valgrind tool for Herbie             local-op.c ---*/
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

#include "local-op.h"
#include "mathreplace.h"
#include "../../helper/ir-info.h"
#include "error.h"
#include "influence-op.h"
#include "../../options.h"
#include "pub_tool_libcprint.h"

double execLocalOp(ShadowOpInfo* info, Real realVal,
                   ShadowValue* res, ShadowValue** args){
  if (no_reals) return 0;
  int nargs = numFloatArgs(info);
  double exactRoundedArgs[4];
  for(int i = 0; i < nargs; ++i){
    exactRoundedArgs[i] = getDouble(args[i]->real);
  }
  double locallyApproximateResult;
  if (info->op_code == 0x0){
    locallyApproximateResult =
      runEmulatedWrappedOp(info->op_type, exactRoundedArgs);
  } else {
    locallyApproximateResult =
      runEmulatedOp(info->op_code, exactRoundedArgs);
  }
  return updateError(&(info->agg.local_error), realVal, locallyApproximateResult);
}
