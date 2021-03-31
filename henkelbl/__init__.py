# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
from io import StringIO
import requests

def binding_en(element='Fe', input_en=100, verbose=True):
    r = requests.post('https://henke.lbl.gov/cgi-bin/pert_cgi.pl', data={'Element': element, 'Energy': str(input_en)})
    splitted_text = r.text.split('<li>')
    if len(splitted_text) == 1:
        print('Element not defined...')
        return {}
    else:
        out_dict = {'Element': element}
        out_dict['Energy']= input_en
        for line in splitted_text:
            if 'Delta' in line:
                delta = float(line.split()[2])
                out_dict['Delta'] = delta
                if verbose:
                    print('Delta: {:.4e}'.format(delta))
            if 'Beta' in line:
                beta = float(line.split()[2])
                out_dict['Beta'] = beta
                if verbose:
                    print('Beta: {:.4e}'.format(beta))
        #--------------------------------------------#
        splitted_text = r.text.split('pre>')
        raw_energies = splitted_text[1]
        for line in raw_energies.splitlines():
            if len(line) > 3:
                line_parts = line.split()
                edge = line_parts[0]
                energy = float(line_parts[1]) #eV
                wavelen = 1239.84/energy #eV to nm
                out_dict[edge] = energy
                if verbose:
                    print('{:s}: {:.3f} eV ({:.3f} nm)'.format(edge, energy, wavelen))
        return out_dict

def get_filter(element=['Al'], thick=[0.2], scan=(45, 75, 100), eV=True, plot=True):
    data = {}
    output = {}
    for i in range(len(element)):
        print('Progress: {:.1f} %'.format(1e2*(i+1)/len(element)))
        data['Material'] = 'Enter+Formula'
        data['Formula'] = element[i]
        data['Density'] = '-1'
        data['Thickness'] = str(thick[i])
        data['Scan'] = 'Energy'
        data['Min'] = str(scan[0])
        data['Max'] = str(scan[1])
        data['Npts'] = str(scan[2])
        data['Plot'] = 'Linear'
        data['Output'] = 'Plot'
        payload = ''
        for key in data.keys():
            payload += key + '=' + data[key] + '&'
        payload = payload[:-1]
        
        r_1 = requests.post('https://henke.lbl.gov/cgi-bin/filter.pl', data=payload, headers={'Content-Type': 'application/x-www-form-urlencoded'})
        splitted_text = r_1.text.split('"')
        for part in splitted_text:
            if '.dat' in part:
                address = 'https://henke.lbl.gov' + part
        r_2 = requests.get(address)
        values = np.genfromtxt(StringIO(r_2.text), skip_header=2)
        key = element[i] + '_{:.1f}'.format(1e3*thick[i])
        output[key] = {}
        output[key]['Element'] = element[i]
        output[key]['Thickness'] = 1e3*thick[i]
        output[key]['Energy'] = values[:, 0]
        output[key]['Wavelength'] = 1239.84/values[:, 0]
        output[key]['Transmission'] = values[:, 1]
    
    if plot:
        # style = plt.style.available[5]
        # plt.style.use('tableau-colorblind10')
        fontsize = 16
        fig1 = plt.figure(figsize=(10, 8))
        ax1_1 = fig1.add_subplot(1,1,1)
        for key in output.keys():
            if eV:
                x_axis = output[key]['Energy']
                x_label = 'Energy (eV)'
            else:
                x_axis = output[key]['Wavelength']
                x_label = 'Wavelength (nm)'
            label = output[key]['Element'] + ' - {:.1f} nm'.format(output[key]['Thickness'])
            ax1_1.plot(x_axis, output[key]['Transmission'], '-', label=label)
        ax1_1.set_ylim(0, 1)
        ax1_1.tick_params(axis='both', labelsize=fontsize)
        ax1_1.set_xlabel(x_label, fontsize=fontsize)
        ax1_1.set_ylabel('Transmittivity', fontsize=fontsize)
        ax1_1.legend(loc='best', fontsize=fontsize)
        ax1_1.grid(True)
        plt.tight_layout()
        plt.show()
    
    return output

def get_multilayer(materials=('Si','Mo','SiO2'), period=6.9, gamma=0.4, rep=40, pol=1, energy=(85, 100, 100), angle=90, eV=True, plot=True):
    """
    1) materials = (TOP, BOTTOM, SUBSTRATE)
    2) period in nm
    3) gamma = (bottom layer)/period
    4) (-1 < pol < 1) where s=1, p=-1 and unpolarized=0
    5) The incidence angle is measured relative to the surface (NOT the surface normal)
    6) energy in eV
    7) angle in deg
    """

    data = {}
    data['Layer2'] = materials[0]
    data['Density2'] = '-1'
    data['Layer1'] = materials[1]
    data['Density1'] = '-1'
    data['Thick'] = str(period)
    data['Gamma'] = str(gamma)
    data['Sigma'] = '0'
    data['Ncells'] = str(rep)
    data['Substrate'] = materials[2]
    data['Sdensity'] = '-1'
    data['Pol'] = str(pol)
    if np.size(energy) == 3:
        data['Scan'] = 'Energy'
        data['Min'] = str(energy[0])
        data['Max'] = str(energy[1])
        data['Npts'] = str(energy[2])
        data['temp'] = 'Angle+(deg)'
        data['Fixed'] = str(angle)
    else:
        data['Scan'] = 'Angle'
        data['Min'] = str(angle[0])
        data['Max'] = str(angle[1])
        data['Npts'] = str(angle[2])
        data['temp'] = 'Energy+(eV)'
        data['Fixed'] = str(energy)
    data['Plot'] = 'Linear'
    data['Output'] = 'Plot'
    payload = ''
    for key in data.keys():
        payload += key + '=' + data[key] + '&'
    payload = payload[:-1]
        
    r_1 = requests.post('https://henke.lbl.gov/cgi-bin/multi.pl', data=payload, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    splitted_text = r_1.text.split('"')
    for part in splitted_text:
        if '.dat' in part:
            address = 'https://henke.lbl.gov' + part
    r_2 = requests.get(address)
    values = np.genfromtxt(StringIO(r_2.text), skip_header=2)
    thick_bot = gamma*period
    thick_top = period - thick_bot
    if np.size(energy) == 3:
        title = '[{:s} ({:.1f} nm) | {:s} ({:.1f} nm)]x{:d} on {:s} at {:.2f} deg'.format(materials[0], thick_top, materials[1], thick_bot, rep, materials[2], angle)
        if eV:
            x_label = 'Energy (eV)'
        else:
            values[:, 0] = 1239.84/values[:, 0]
            x_label = 'Wavelength (nm)'
    else:
        title = '[{:s} ({:.1f} nm) | {:s} ({:.1f} nm)]x{:d} on {:s} at {:.2f} eV'.format(materials[0], thick_top, materials[1], thick_bot, rep, materials[2], energy)
        x_label = 'Inc. angle (deg)'
    
    if plot:
        fontsize = 16
        fig1 = plt.figure(figsize=(10, 8))
        ax1_1 = fig1.add_subplot(1,1,1)
        ax1_1.plot(values[:, 0], values[:, 1], '-b')
        # ax1_1.set_ylim(0, 1)
        ax1_1.tick_params(axis='both', labelsize=fontsize)
        ax1_1.set_title(title, fontsize=fontsize+2)
        ax1_1.set_xlabel(x_label, fontsize=fontsize)
        ax1_1.set_ylabel('Reflectivity', fontsize=fontsize)
        ax1_1.grid(True)
        plt.tight_layout()
        plt.show()
    
    return values

def get_singlelayer(materials=('Au','Si'), thick=30, pol=1, energy=(85, 100, 100), angle=90, eV=True, plot=True):
    """
    1) materials = (LAYER, SUBSTRATE)
    2) thickness in nm
    3) (-1 < pol < 1) where s=1, p=-1 and unpolarized=0
    4) The incidence angle is measured relative to the surface (NOT the surface normal)
    5) energy in eV
    6) angle in deg
    """

    data = {}
    data['Layer'] = materials[0]
    data['Ldensity'] = '-1'
    data['Thick'] = str(thick)
    data['Sigma1'] = '0'
    data['Substrate'] = materials[1]
    data['Sdensity'] = '-1'
    data['Sigma2'] = '0'
    data['Pol'] = str(pol)
    if np.size(energy) == 3:
        data['Scan'] = 'Energy'
        data['Min'] = str(energy[0])
        data['Max'] = str(energy[1])
        data['Npts'] = str(energy[2])
        data['temp'] = 'Angle+(deg)'
        data['Fixed'] = str(angle)
    else:
        data['Scan'] = 'Angle'
        data['Min'] = str(angle[0])
        data['Max'] = str(angle[1])
        data['Npts'] = str(angle[2])
        data['temp'] = 'Energy+(eV)'
        data['Fixed'] = str(energy)
    data['Plot'] = 'Linear'
    data['Output'] = 'Plot'
    payload = ''
    for key in data.keys():
        payload += key + '=' + data[key] + '&'
    payload = payload[:-1]
        
    r_1 = requests.post('https://henke.lbl.gov/cgi-bin/laymir.pl', data=payload, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    splitted_text = r_1.text.split('"')
    for part in splitted_text:
        if '.dat' in part:
            address = 'https://henke.lbl.gov' + part
    r_2 = requests.get(address)
    values = np.genfromtxt(StringIO(r_2.text), skip_header=2)
    if np.size(energy) == 3:
        title = '{:s} ({:.1f} nm) on {:s} at {:.2f} deg'.format(materials[0], thick, materials[1], angle)
        if eV:
            x_label = 'Energy (eV)'
        else:
            values[:, 0] = 1239.84/values[:, 0]
            x_label = 'Wavelength (nm)'
    else:
        title = '{:s} ({:.1f} nm) on {:s} at {:.2f} eV'.format(materials[0], thick, materials[1], energy)
        x_label = 'Inc. angle (deg)'
    
    if plot:
        fontsize = 16
        fig1 = plt.figure(figsize=(10, 8))
        ax1_1 = fig1.add_subplot(1,1,1)
        ax1_1.plot(values[:, 0], values[:, 1], '-b')
        # ax1_1.set_ylim(0, 1)
        ax1_1.tick_params(axis='both', labelsize=fontsize)
        ax1_1.set_title(title, fontsize=fontsize+2)
        ax1_1.set_xlabel(x_label, fontsize=fontsize)
        ax1_1.set_ylabel('Reflectivity', fontsize=fontsize)
        ax1_1.grid(True)
        plt.tight_layout()
        plt.show()
    
    return values

def get_refrIndex(material='Fe', energy=(30, 130, 100), eV=True, plot=True):

    data = {}
    data['Material'] = 'Enter+Formula'
    data['Formula'] = material
    data['Density'] = '-1'
    data['Scan'] = 'Energy'
    data['Min'] = str(energy[0])
    data['Max'] = str(energy[1])
    data['Npts'] = str(energy[2])
    data['Output'] = 'Text+File'
    payload = ''
    for key in data.keys():
        payload += key + '=' + data[key] + '&'
    payload = payload[:-1]
        
    r_1 = requests.post('https://henke.lbl.gov/cgi-bin/getdb.pl', data=payload, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    
    splitted_text = r_1.text.split('"')
    for part in splitted_text:
        if '.dat' in part:
            address = 'https://henke.lbl.gov' + part
    r_2 = requests.get(address)
    values = np.genfromtxt(StringIO(r_2.text), skip_header=2)
    
    if plot:
        
        title = 'Refractive index for {:s} (1 - Delta - i*Beta)'.format(material)
        if eV:
            x_label = 'Energy (eV)'
        else:
            values[:, 0] = 1239.84/values[:, 0]
            x_label = 'Wavelength (nm)'
        
        fontsize = 16
        fig1 = plt.figure(figsize=(10, 8))
        ax1_1 = fig1.add_subplot(1,1,1)
        ax1_1.semilogy(values[:, 0], values[:, 1], '-b', label='Delta')
        ax1_1.semilogy(values[:, 0], values[:, 2], '-r', label='Beta')
        ax1_1.tick_params(axis='both', labelsize=fontsize)
        ax1_1.set_title(title, fontsize=fontsize+2)
        ax1_1.set_xlabel(x_label, fontsize=fontsize)
        ax1_1.set_ylabel('Delta, Beta', fontsize=fontsize)
        ax1_1.grid(True)
        ax1_1.legend(loc='best', fontsize=fontsize)
        plt.tight_layout()
        plt.show()
    
    return values