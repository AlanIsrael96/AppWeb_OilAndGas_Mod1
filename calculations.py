"""Funciones de cálculo para los módulos técnicos de la aplicación."""

from __future__ import annotations

import numpy as np


def composite_ipr(pr: float, pb: float, productivity_index: float, pwf):
    """Calcula la IPR compuesta para un yacimiento inicialmente subsaturado."""
    pwf_array = np.asarray(pwf, dtype=float)
    qb = productivity_index * (pr - pb)
    qmax = qb + (productivity_index * pb / 1.8)
    above_bubble = productivity_index * (pr - pwf_array)
    below_bubble = qb + (productivity_index * pb / 1.8) * (
        1 - 0.2 * (pwf_array / pb) - 0.8 * (pwf_array / pb) ** 2
    )
    rate = np.where(pwf_array >= pb, above_bubble, below_bubble)
    return rate, qb, qmax


def hydrostatic_pressure(mud_weight: float, tvd: float, formation_pressure: float):
    """Devuelve gradiente, presión hidrostática y diferencial de presión."""
    gradient = 0.052 * mud_weight
    pressure = gradient * tvd
    return gradient, pressure, pressure - formation_pressure


def volumetric_oip(area: float, gross_thickness: float, ntg: float, porosity: float,
                   swi: float, boi: float, recovery_factor: float):
    """Estima POES y petróleo recuperable por el método volumétrico."""
    net_thickness = gross_thickness * ntg
    oip = 7758 * area * net_thickness * porosity * (1 - swi) / boi
    return net_thickness, oip, oip * recovery_factor
