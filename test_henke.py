import henkelbl as hl
import matplotlib.pyplot as plt

#%% Binding energy for a given element

en = hl.bindingEn('Al', 50)

#%% Filters: transmissions for a list of elements (not a stack)

plt.close('all')

element = ['Al', 'Al', 'Al', 'Al', 'Zr', 'Zr', 'Zr', 'Pd', 'Si', 'Sn', 'In']
thick = [0.1, 0.2, 0.4, 0.78, 0.1, 0.2, 0.3, 0.2, 0.19, 0.2, 0.18]
data = hl.get_filter(element, thick, scan=(20, 220, 200), eV=False)

ax = plt.gca()
ax.axvline(20, c='k', ls='--')
ax.axvline(40, c='k', ls='--')

#%% Thick mirror for a list of elements

plt.close('all')

element = ['Au', 'Au']
roughness = [0, 0]
pol = [1, -1] #(-1 < pol < 1) where s=1, p=-1 and unpolarized=0
energy = (40, 100, 100) #tuple or single value, in eV
angle = 42  #tuple or single value, in deg
data = hl.get_thickMirror(element, roughness, pol, energy, angle)

ax = plt.gca()
ax.set_ylim(0, 0.2)
ax.axvline(45, c='k')
ax.axvline(90, c='k')
plt.tight_layout()

#%% Multilayer mirror

plt.close('all')

materials = ('Si','Mo','SiO2') #(top, bottom, substrate)
period = 6.9 #nm
bottom_fraction = 0.4 #bottom thickness = bottom_fraction*period
reps = 40 #number of repetitions
pol = 1 #(-1 < pol < 1) where s=1, p=-1 and unpolarized=0
energy = 95 #tuple or single value, in eV
angle = (10, 80, 200) #tuple or single value, in deg
ml = hl.get_multiLayer(materials, period, bottom_fraction, reps, pol, energy, angle)

#%% Single layer mirror

plt.close('all')

materials = ('Au','SiO2') #(layer, substrate)
thickness = 30 #nm
pol = 1 #(-1 < pol < 1) where s=1, p=-1 and unpolarized=0
energy = 55 #tuple or single value, in eV
angle = (40, 75, 150) #tuple or single value, in deg
ml = hl.get_singleLayer(materials, thickness, pol, energy, angle)

#%% Refractive index

plt.close('all')

refr = hl.get_refrIndex('Al', (30, 130, 100))

#%% Attenuation length

plt.close('all')

att = hl.get_attLength('Al', (30, 130, 100))