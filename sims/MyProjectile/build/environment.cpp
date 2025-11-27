// Merged environment module
#include "class_hierarchy.hpp"

void Ball::def_environment()
{
	ball[0].init("grav","D",0,"Gravity acceleration - m/s^2","environment","out","");
	ball[12].init("rho",0,"Air density - kg/m^3","out","","");
}

void Ball::environment(double int_step)
{
    // Read parameters (will be set from input.asc)
    double grav = ball[0].real();
    double rho = ball[12].real();

    ball[0].gets(grav);
    ball[12].gets(rho);
}
