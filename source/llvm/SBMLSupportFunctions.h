/*
 * SBMLSupportFunctions.h
 *
 *  Created on: Aug 22, 2013
 *      Author: andy
 */

#ifndef SBMLSUPPORTFUNCTIONS_H_
#define SBMLSUPPORTFUNCTIONS_H_

namespace sbmlsupport
{

double trunc(double d);

double poweri(double x, int y);

double spf_abs(double x);

double powerf(double base, double exponent);



double factorial(double a);

double root(double a, double b);


double sec(double a);

//// Cotangent
double cot(double a);
//
//// Inverse cotangent
double arccot(double a);

//// Inverse cotangent - ratio numerator and denominator provided
double arccot2(double a, double b);

//// Inverse secant
double asec(double a);

//// Cosecant
double csc(double a);

//// Inverse cosecant
double acsc(double a);

//// Hyperbolic secant of a double number
double sech(double a);

//// Inverse hyperbolic secant of a double number
double asech(double a);

double arcsech(double a);

//// Hyperbolic cosecant of a double number
double csch(double a);
//// Inverse hyperbolic cosecant of a double number
double arccsc(double a);
//// Inverse hyperbolic cosecant of a double number
double arccsch(double a);

//// Hyperbolic cotangent of a double number
double coth(double a);

//// Inverse hyperbolic cotangent of a double number
double arccoth(double a);

//// Inverse hyperbolic functions
//// --------------------------------------------------------------
//// Inverse hyperbolic sine of a double number
double arcsinh(double a);

//// Inverse hyperbolic cosine of a double number
double arccosh(double a);

//// Inverse hyperbolic tangent of a double number
double arctanh(double a);



} /* namespace sbmlsupport */
#endif /* SBMLSUPPORTFUNCTIONS_H_ */
