//==========================================================================
//   CEXCEPTION.H - header for
//                             OMNeT++
//            Discrete System Simulation in C++
//
//
//  Exception class
//
//==========================================================================

/*--------------------------------------------------------------*
  Copyright (C) 1992-2001 Andras Varga
  Technical University of Budapest, Dept. of Telecommunications,
  Stoczek u.2, H-1111 Budapest, Hungary.

  This file is distributed WITHOUT ANY WARRANTY. See the file
  `license' for details on this and other legal matters.
*--------------------------------------------------------------*/

#ifndef __CEXCEPTION_H
#define __CEXCEPTION_H

#include <stdarg.h>  // for va_list
#include "defs.h"
#include "util.h"

class cModule;

class SIM_API cException
{
  protected:
    int errorcode;
    opp_string errormsg;
    cModule *module;

  public:
    /**
     * Error is identified by an error code, and the message comes from a
     * string table. The error string may expect printf-like arguments
     * (%s, %d) which also have to be passed to the constructor.
     */
    cException(int errcode,...);

    /**
     * To be called like printf(). The error code is set to eCUSTOM.
     */
    cException(const char *msg,...);

    /**
     * Returns the error code.
     */
    int errorCode() {return errorcode;}

    /**
     * Returns the text of the error.
     */
    const char *errorMessage() {return errormsg;}

    /**
     * Returns the module where the exception occurred.
     */
    cModule *errorModule() {return module;}
};

#endif
