import p2api
from astroquery.simbad import Simbad
import numpy as np
from getpass import getpass
from astropy.time import Time

Simbad.add_votable_fields('flux(V)')
Simbad.add_votable_fields('flux(K)')
Simbad.add_votable_fields('flux(H)')
Simbad.add_votable_fields('pmdec')
Simbad.add_votable_fields('pmra')

class CreateOBapi():
    def __init__(self, dictionary):
        """
        Create an OB for exoplanet observation with GRAVITY
        Input has to be a dictionary
        """
        print('\n\nESO P2 credentials')
        user = input('Username: ')
        password = getpass()

        if user == 'demo':
            print('Will use demo version of p2')
            print('Be careful, OB will be public at:')
            print('https://www.eso.org/p2demo/home')
            api = p2api.ApiConnection('demo', '52052', 'tutorial')
            self.demo = True
        else:
            self.demo = False
            try:
                api = p2api.ApiConnection('production', user, password)
            except(p2api.P2Error):
                print('Cannot login to P2')
                return None

        # Create OB
        header = dictionary['template1']
        if header['type'] != 'header':
            raise ValueError('First template in file %s has to be a header template'
                             % filename)

        star = header['OB name']
        runID = header['run ID']
        obs_date = header['Obs time']
        mode = header['mode']
        template_ob_id = header["template_ob_id"]
        calib = header["calib"]
        self.api = api
        self.target = star
        self.time_now = Time.now()
        if obs_date is None:
            obs_date = str(self.time_now.datetime.date())
        obs_date = obs_date.replace('-', '')
        # Get the information of the star from Simbad
        self.searchSimbad(star)

        if self.demo:
            runID = '60.A-9252(M)'

        myrun = find_runID(runID, api)
        runContainerId = myrun['containerId']

        if self.demo:
            runContainerId = 2331868

        if check_dither(dictionary) is False:
            ob_name = star + '_' + mode + '_' + obs_date
            ob_info = find_item(ob_name, runContainerId, api, "OB")
            if not ob_info is None:
                obRename = input('The OB exists, do you want to add suffix to it? [y,n] ')
                if obRename == 'y':
                    ob_suf = 0
                    ob_name = star + '_' + obs_date + '_{0}'.format(ob_suf)
                    # Check and increase the suffix number if there is still conflict.
                    while(not find_item(ob_name, runContainerId, api, "OB") is None):
                        ob_suf += 1
                        ob_name = star + '_' + obs_date + '_{0}'.format(ob_suf)
                else:
                    ob, obVersion = api.getOB(ob_info['obId'])
                    try: # Try to delete the original OB
                        print("Try to replace the OB.")
                        api.deleteOB(ob['obId'], obVersion)
                    except:
                        raise("Cannot replace the OB, please consider to add suffix to the name.")
            print('\nCreating OB: %s\n' % ob_name)
            self.createOB(runContainerId, ob_name, template_ob_id)
            # Do the individual templates
            for idx in range(1, len(dictionary), 1):
                templatename = 'template%i' % (idx+1)
                template = dictionary[templatename]
                if template['type'] == 'acquisition':
                    self.createACQ(template, calib)
                elif template['type'] == 'dither':
                    self.createDITHER(template)
                elif template['type'] == 'observation':
                    self.createEXP(template)
                elif template['type'] == 'swap':
                    self.createSWAP(template)
                else:
                    raise ValueError('Type of %s not known, has to be acquisition, dither or observation' % templatename)
            print('\n\nOB is created in P2')
        else: # There is dithering
            folderName = star + '_' + mode + '_' + obs_date
            folder_info = find_item(folderName, runContainerId, api, "Folder")
            if not folder_info is None:
                folderRename = input('The folder exists, do you want to add suffix to it? [y,n] ')
                if folderRename == 'y':
                    folder_suf = 0
                    folderName = star + '_' + mode + '_' + obs_date + '_{0}'.format(folder_suf)
                    while(not find_item(folderName, runContainerId, api, "Folder") is None):
                        folder_suf += 1
                        folderName = star + '_' + mode + '_' + obs_date + '_{0}'.format(folder_suf)
            folder, folderVersion = api.createFolder(runContainerId, folderName)
            folderContainerId = folder["containerId"]
            dither_counter = 0
            for idx in range(1, len(dictionary), 1):
                templatename = 'template%i' % (idx+1)
                template = dictionary[templatename]
                if template['type'] == 'acquisition':
                    ob_name = '{0}_dither_{1}'.format(template['target name'], dither_counter)
                    dither_counter += 1
                    self.createOB(folderContainerId, ob_name, template_ob_id)
                    self.createACQ(template, calib)
                elif template['type'] == 'dither':
                    ob_name = '{0}_dither_{1}'.format(template['name science'], dither_counter)
                    dither_counter += 1
                    self.createOB(folderContainerId, ob_name, template_ob_id)
                    self.createDITHER(template, calib)
                elif template['type'] == 'observation':
                    self.createEXP(template)
                elif template['type'] == 'swap':
                    self.createSWAP(template)
                else:
                    raise ValueError('Type of %s not known, has to be acquisition, dither or observation' % templatename)

    def searchSimbad(self, star):
        """
        Search the information of the star from Simbad.
        """
        # correct for the actual name:
        if star == 'betapic':
            star = 'Beta Pictoris'
        star_table = Simbad.query_object(star)
        if star_table is None:
            raise ValueError('Input not known by Simbad')
        # Get the information from Simbad output
        targ_ra = star_table['RA'][0].replace(' ', ':')[:-1]
        targ_dec = star_table['DEC'][0].replace(' ', ':')
        targ_pmra = star_table['PMRA'][0]/1000
        targ_pmdec = star_table['PMDEC'][0]/1000
        targ_magK = round(star_table['FLUX_K'][0].item(),2)
        targ_magV = round(star_table['FLUX_V'][0].item(),2)
        targ_magH = round(star_table['FLUX_H'][0].item(),2)
        # Make up the lacking information
        if np.ma.is_masked(star_table['FLUX_K']):
            print('No K-Band magnitude in Simbad...')
            targ_magK = float(input('K-Band magnitude = '))
        if np.ma.is_masked(star_table['FLUX_H']):
            print('No H-Band magnitude in Simbad...')
            targ_magH = float(input('H-Band magnitude = '))
        if np.ma.is_masked(star_table['FLUX_V']):
            print('No V-Band magnitude in Simbad...')
            targ_magV = float(input('V-Band magnitude = '))
        if np.ma.is_masked(targ_pmra) or np.ma.is_masked(targ_pmdec):
            print('No proper motion given, assume 0.0')
            targ_pmdec = 0.0
            targ_pmra = 0.0
        # Print the information
        print('\nGetting Simbad values for %s:' % star)
        print('Position RA  = %s' % targ_ra)
        print('Position DEC = %s' % targ_dec)
        print('Proper motion RA  = %s as/yr' % targ_pmra)
        print('Proper motion DEC = %s as/yr' % targ_pmdec)
        print('K magnitude = %.2f' % targ_magK)
        print('H magnitude = %.2f' % targ_magH)
        print('V magnitude = %.2f' % targ_magV)
        self.targ_ra = targ_ra
        self.targ_dec = targ_dec
        self.targ_pmra = targ_pmra
        self.targ_pmdec = targ_pmdec
        self.targ_magK = targ_magK
        self.targ_magV = targ_magV
        self.targ_magH = targ_magH

    def createOB(self, containerId, ob_name, template_ob_id=None):
        """
        Create an OB.
        """
        if template_ob_id is None:
            ob, obVersion = self.api.createOB(containerId, ob_name)
            self.new_instrument_package = False
            print("Create new OB ID: {0}".format(ob["obId"]))
        else:
            ob, obVersion = self.api.duplicateOB(template_ob_id, containerId)
            self.new_instrument_package = True
            print("Duplicate OB with ID: {0} --> {1}".format(template_ob_id, ob["obId"]))
            ob["name"] = ob_name
        ob['constraints']['skyTransparency'] = 'Clear'
        ob['obsDescription']['name'] = ob_name
        ob['obsDescription']['userComments'] = u'Created by exoGRAVITY script {0}.'.format(str(self.time_now.datetime))
        ob['target']['name'] = self.target
        ob['target']['ra'] = self.targ_ra
        ob['target']['dec'] = self.targ_dec
        ob['target']['properMotionRa'] = self.targ_pmra
        ob['target']['properMotionDec'] = self.targ_pmdec
        ob, obVersion = self.api.saveOB(ob, obVersion)
        self.obId = ob['obId']

    def createACQ(self, tempdict, calib):
        """
        Create aquisition template and adds it to OB
        """
        try:
            acqTpl, acqTplVersion = self.api.createTemplate(self.obId, 'GRAVITY_dual_acq')
        except(p2api.P2Error):
            print('Something went wrong, there is already an aquisition')
            return None

        resolution = tempdict['resolution']
        wollaston = tempdict['wollaston']
        baseline = tempdict['baseline']
        vltitype = tempdict['vltitype']
        sobj_x = tempdict['RA offset']
        sobj_y = tempdict['DEC offset']
        first_planet = tempdict['target name']
        acqDict = {
            'SEQ.FT.ROBJ.NAME': self.target,
            'SEQ.FT.ROBJ.MAG': self.targ_magK,
            'SEQ.FT.ROBJ.DIAMETER': 0.0,
            'SEQ.FT.ROBJ.VIS': 1.0,
            'SEQ.FT.MODE': 'AUTO',
            'SEQ.INS.SOBJ.NAME': first_planet,
            'SEQ.INS.SOBJ.MAG': self.targ_magK,
            'SEQ.INS.SOBJ.DIAMETER': 0.0,
            'SEQ.INS.SOBJ.VIS': 1.0,
            'SEQ.INS.SOBJ.X': sobj_x,
            'SEQ.INS.SOBJ.Y': sobj_y,
            'SEQ.FI.HMAG': self.targ_magH,
            'TEL.TARG.PARALLAX': 0.0,
            'INS.SPEC.RES': resolution,
            'INS.FT.POL': wollaston,
            'INS.SPEC.POL': wollaston,
            'COU.AG.GSSOURCE': 'SCIENCE',
            'COU.AG.ALPHA': '00:00:00.000',
            'COU.AG.DELTA': '00:00:00.000',
            'COU.GS.MAG': self.targ_magV,
            'COU.AG.PMA': 0.0,
            'COU.AG.PMD': 0.0,
            'COU.AG.TYPE': 'ADAPT_OPT',
            'ISS.BASELINE': [baseline],
            'ISS.VLTITYPE': [vltitype],
        }
        if self.new_instrument_package is True:
            acqDict['SEQ.ALIGN'] = False
            if calib is False: # This is for planets; Binary calibrator still need PICKFT manually
                acqDict['SEQ.PICKFT'] = "A"
                acqDict['SEQ.PICKSC'] = "F"
        else:
            print("This is still the old instrument package...")
        acqTpl, acqTplVersion  = self.api.setTemplateParams(self.obId, acqTpl, acqDict, acqTplVersion)

    def createDITHER(self, tempdict, calib):
        """
        Create dither template and adds it to OB
        """
        try:
            acqTpl, acqTplVersion = self.api.createTemplate(self.obId, 'GRAVITY_dual_acq_dither')
        except(p2api.P2Error):
            print('Something went wrong, dither should be in the beginning?')
            return None
        acqDict = {
            'SEQ.FT.ROBJ.NAME': self.target,
            'SEQ.FT.ROBJ.MAG': self.targ_magK,
            'SEQ.FT.ROBJ.DIAMETER': 0.0,
            'SEQ.FT.ROBJ.VIS': 1.0,
            'SEQ.FT.MODE': 'AUTO',
            'SEQ.INS.SOBJ.NAME': tempdict['name science'],
            'SEQ.INS.SOBJ.MAG': tempdict['mag science'],
            'SEQ.INS.SOBJ.DIAMETER': 0.0,
            'SEQ.INS.SOBJ.VIS': 1.0,
            'SEQ.INS.SOBJ.X': tempdict['RA offset'],
            'SEQ.INS.SOBJ.Y': tempdict['DEC offset'],
            'SEQ.DITHER.X': 0.0,
            'SEQ.DITHER.Y': 0.0,
        }
        if self.new_instrument_package is True:
            acqDict['SEQ.ALIGN'] = False
            if calib is False: # This is for planets; Binary calibrator still need PICKFT manually
                acqDict['SEQ.PICKFT'] = "A"
                acqDict['SEQ.PICKSC'] = "F"
        else:
            print("This is still the old instrument package...")
        acqTpl, acqTplVersion  = self.api.setTemplateParams(self.obId, acqTpl, acqDict, acqTplVersion)

    def createEXP(self, tempdict):
        """
        Create exposure template and adds it to OB
        """

        scTpl, scTplVersion = self.api.createTemplate(self.obId, 'GRAVITY_dual_obs_exp')
        reloff_x = [tempdict['RA offset']]
        reloff_y = [tempdict['DEC offset']]
        dit = tempdict['DIT']
        ndit = tempdict['NDIT']
        sequence = tempdict['sequence']

        scTpl, scTplVersion = self.api.setTemplateParams(self.obId, scTpl, {
            'DET2.DIT' : dit,
            'DET2.NDIT.OBJECT' : ndit,
            'DET2.NDIT.SKY' : ndit,
            'SEQ.HWPOFF' : [0.0],
            'SEQ.OBSSEQ' : sequence,
            'SEQ.RELOFF.X' : reloff_x,
            'SEQ.RELOFF.Y' : reloff_y,
            'SEQ.SKY.X' : 2000.0,
            'SEQ.SKY.Y' : 2000.0
        }, scTplVersion)

    def createSWAP(self, tempdict):
        """
        Create swap template and adds it to OB.
        """
        scTpl, scTplVersion = self.api.createTemplate(self.obId, 'GRAVITY_dual_obs_swap')
        scTpl, scTplVersion = self.api.setTemplateParams(self.obId, scTpl, {
            'DET1.DIT'   : '0.7',
            'SEQ.SKY.X'  : '2000',
            'SEQ.SKY.Y'  : '2000',
            'SEQ.SWAP'   : 'T',
            'SEQ.PICKFT' : 'T',
            'SEQ.TAKESKY': 'F'
        }, scTplVersion)


def find_item(item_name, containerId, api, item_type=None):
    """
    Look for the item name in a container.

    Returns
    -------
    it : dict or None
        Return the item if it is found. Otherwise, return None.
    """
    items, itemsVersion = api.getItems(containerId)
    for it in items:
        b_name = it['name'] == item_name
        if item_type is None:
            b_type = True
        else:
            b_type = it['itemType'] == item_type
        if (b_name & b_type):
            return it
    return None

def find_runID(run_id, api):
    """
    Get the run with the run ID.

    Returns
    -------
    run : dict or None
        The information of the run. If the run ID is not found, return None.
    """
    runs, _ = api.getRuns()
    for run in runs:
        if run['progId'] == run_id:
            return run
    return None

def check_dither(seq):
    """
    Check whether there is dithering in the sequence.

    Parameters
    ----------
    seq : dict
        The sequence of observation templates.

    Returns
    -------
    True if the sequence contains a dither template, False otherwise.
    """
    for s in seq:
        if seq[s]['type'] == "dither":
            return True
    return False
