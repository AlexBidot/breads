import numpy as numpy
from BayesicFitting import EtalonModel
from astropy import units
import math
from BayesicFitting.source import Tools
from BayesicFitting.source.NonLinearModel import NonLinearModel

class PositiveEtalonModel( NonLinearModel ):
    """
    Etalon Model.

        f( x:p ) = p_0 / ( 1.0 + p_1^2 * sin^2( &pi; p_2 x + p_3 ) )

    where
        p_0 = amplitude
        p_1^2 = finesse,
        p_2 = frequency in 1/wavenumber
        p_3 = phase,
    As always x = input; it is in wavenumbers

    The parameters are initialized at {1.0, 1.0, 1.0, 0.0}. It is a non-linear model.

    Attributes from Model
    ---------------------
        npchain, parameters, stdevs, xUnit, yUnit

    Attributes from FixedModel
    --------------------------
        npmax, fixed, parlist, mlist

    Attributes from BaseModel
    --------------------------
        npbase, ndim, priors, posIndex, nonZero, tiny, deltaP, parNames

    Examples
    --------
    >>> fpm = EtalonModel( )
    >>> print( fpm.npchain )
    4
    >>> pars = [1.0, 30.0, 1.0, 0.0]
    >>> fpm.parameters = pars
    >>> print( fpm( numpy.arange( 101, dtype=float ) ) )     # etalon with 10 periods

    """

    def __init__( self, copy=None, **kwargs ):
        """
        Etalon model.

        Number of parameters is 4.

        Parameters
        ----------
        copy : EtalonModel
            to be copied
        fixed : None or dictionary of {int:float|Model}
            int         index of parameter to fix permanently.
            float|Model values for the fixed parameters.
            Attribute fixed can only be set in the constructor.
            See: @FixedModel

        """
        param = [1.0, 1.0, 1.0, 0.0]
        names = ["amplitude", "finesse", "frequency", "phase"]
        super( PositiveEtalonModel, self ).__init__( 4, copy=copy, params=param,
                    names=names, **kwargs )


    def copy( self ):
        """ Copy method.  """
        return PositiveEtalonModel( copy=self )

    def baseResult( self, xdata, params ):
        """
        Returns the result of the model function.

        Parameters
        ----------
        xdata : array_like
            values at which to calculate the result
        params : array_like
            values for the parameters.

        """
        x = math.pi * xdata * params[2] + params[3]
        sx = numpy.sin( x )
        return params[0] / ( 1.0 + params[1] * params[1] * sx * sx )

    def baseDerivative( self, xdata, params ):
        """
        Returns the derivative of f to x (df/dx) at the input values.

        Parameters
        ----------
        xdata : array_like
            values at which to calculate the result
        params : array_like
            values for the parameters.

        """
        x = math.pi * xdata * params[2] + params[3]
        sx = numpy.sin( x )
        dd = 1 + params[1] * params[1] * sx * sx
        dd *= dd
        return - 2 * math.pi * params[0] * params[1] * params[1] * params[2] * sx * numpy.cos( x ) / dd


    def basePartial( self, xdata, params, parlist=None ):
        """
        Returns the partials at the input values.

        Parameters
        ----------
        xdata : array_like
            values at which to calculate the result
        params : array_like
            values for the parameters.
        parlist : array_like
            list of indices active parameters (or None for all)

        """
        np = self.npbase if parlist is None else len( parlist )
        partial = numpy.ndarray( ( Tools.length( xdata ), np ) )

        x = math.pi * xdata * params[2] + params[3]
        sx = numpy.sin( x )
        s2 = sx * sx
        dd = 1.0 / ( 1 + params[1] * params[1] * s2 )
        d2 = dd * dd
        p3 = - 2 * params[0] * params[1] * params[1] * sx * numpy.cos( x ) * d2

        parts = { 0 : ( lambda: dd ),
                  1 : ( lambda: - 2 * params[0] * params[1] * s2 * d2 ),
                  2 : ( lambda: math.pi * xdata * p3 ),
                  3 : ( lambda: p3 ) }

        if parlist is None :
            parlist = range( self.npmax )

        for k,kp in enumerate( parlist ) :
            partial[:,k] = parts[kp]()

        return partial

    def baseName( self ):
        """
        Returns a string representation of the model.

        """
        return ( "Etalon: f( x:p ) = p_0 / ( 1 + p_1^2 * sin^2( PI * x * p_2 + p_3 ) )" )

    def baseParameterUnit( self, k ):
        """
        Return the name of a parameter.

        Parameters
        ----------
        k : int
            the kth parameter.

        """
        if k == 0:
            return self.yUnit
        if k == 1:
            return units.Unit( "" )
        if k == 2:
            return units.Unit( units.si.rad ) / self.xUnit
        if k == 3:
            return units.Unit( units.si.rad )
        return self.yUnit


