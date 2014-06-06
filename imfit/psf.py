'''
Created on Sep 25, 2013

@author: andre
'''
from .fitting import Imfit
from .model import SimpleModelDescription
from .lib import function_description
import numpy as np

__all__ = ['gaussian_psf', 'moffat_psf']


FWHM_to_sigma_factor = 2.0 * np.sqrt(2.0 * np.log(2.0))


def gaussian_psf(width, type='fwhm', PA=0.0, ell=0.0, size=31):
    '''
    Creates a 2-D gaussian Point Spread function, to be used
    when creating an :class:`Imfit` object.
    
    Parameters
    ----------
    width: float
        Width (semimajor axis) of the PSF.
        
    type: string, optional
        One of:
            * ``'fwhm'`` : Width is the full width at half maximum of the gaussian (default).
            * ``'sigma'`` : Width is the variance (sigma) of the gaussian.
        
    PA : float, optional
        Position angle of the PSF, in degrees from the Y-axis. Default: ``0.0``.
        
    ell : float, optional
        Ellipticy (:math:`1 - b/a`) of the PSF. Default: ``0.0``.
        
    size : int, optional
        Size of the PSF image. Must be an odd number so that
        the PSF is symmetric. Default: ``31``.
    
    
    Returns
    -------
    psf : 2-D array
        Image of the gaussian.
    '''
    if size % 2 != 1:
        raise ValueError('Size must be an odd number.')
    if type == 'fwhm':
        sigma = width / FWHM_to_sigma_factor
    elif type == 'sigma':
        sigma = width
    else:
        ValueError('type must be either fwhm or sigma.')
    center = (size+1) / 2
    model = SimpleModelDescription()
    model.x0.setValue(center)
    model.y0.setValue(center)
    gaussian = function_description('Gaussian')
    gaussian.I_0.setValue(1.0)
    gaussian.sigma.setValue(sigma)
    gaussian.PA.setValue(PA)
    gaussian.ell.setValue(ell)
    model.addFunction(gaussian)
    imfit = Imfit(model)
    psf_image = imfit.getModelImage(shape=(size,size))
    return psf_image


def moffat_psf(fwhm, beta=3.1, PA=0.0, ell=0.0, size=31):
    '''
    Creates a 2-D Moffat Point Spread function, to be used
    when creating an :class:`Imfit` object.
    
    Parameters
    ----------
    fwhm : float
        Full width ath half maximum (semimajor axis) of the Moffat profile.
        
    beta : float, optional
        The :math:`\\beta` parameter of the Moffat profile. Default: ``3.1``.
        
    PA : float, optional
        Position angle of the PSF, in degrees from the Y-axis. Default: ``0.0``.
        
    ell : float, optional
        Ellipticy (:math:`1 - b/a`) of the PSF. Default: ``0.0``.
        
    size : int, optional
        Size of the PSF image. Must be an odd number so that
        the gaussian is symmetric. Default: ``31``.
    
    
    Returns
    -------
    psf : 2-D array
        Image of the gaussian.
    '''
    if size % 2 != 1:
        raise ValueError('Size must be an odd number.')
    center = (size+1) / 2
    model = SimpleModelDescription()
    model.x0.setValue(center)
    model.y0.setValue(center)
    moffat = function_description('Moffat')
    moffat.I_0.setValue(1.0)
    moffat.fwhm.setValue(fwhm)
    moffat.beta.setValue(beta)
    moffat.PA.setValue(PA)
    moffat.ell.setValue(ell)
    model.addFunction(moffat)
    imfit = Imfit(model)
    psf_image = imfit.getModelImage(shape=(size,size))
    return psf_image
