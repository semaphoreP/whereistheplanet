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
        if obs_date is None:
            time = Time.now()
            obs_date = str(time.datetime.date())
        obs_date = obs_date.replace('-', '')

        if self.demo:
            runID = '60.A-9252(M)'

        ob_name = star + '_' + obs_date
        runs = api.getRuns()

        for run in runs[0]:
            if run['progId'] == runID:
                myrun = run
                break
            if run == runs[0][-1]:
                raise ValueError('Given runID not found')

        runContainerId = myrun['containerId']

        if self.demo:
            runContainerId = 2331868

        OBs = api.getItems(runContainerId)

        newOB = True
        for OB in OBs[0]:
            if OB['name'] == ob_name and OB['itemType'] == 'OB':
                newOB = False
                replaceOB = input('OB already exists, do you want to replace it? [y,n]')
                if replaceOB == 'y':
                    ob, obVersion = api.getOB(OB['obId'])
                    api.deleteOB(ob['obId'], obVersion)
                else:
                    print('Abort. Rename/Delete old OB or give the new one a different name')
                    return None

        print('\nCreating OB: %s\n' % ob_name)
        ob, obVersion = api.createOB(runContainerId, ob_name)

        # Simbad
        # correct for the actual name:
        if star == 'betapic':
            star = 'Beta Pictoris'


        star_table = Simbad.query_object(star)
        if star_table is None:
            raise ValueError('Input not known by Simbad')

        targ_ra = star_table['RA'][0].replace(' ', ':')[:-1]
        targ_dec = star_table['DEC'][0].replace(' ', ':')
        targ_pmra = star_table['PMDEC'][0]/1000
        targ_pmdec = star_table['PMRA'][0]/1000

        targ_magK = round(star_table['FLUX_K'][0].item(),2)
        targ_magV = round(star_table['FLUX_V'][0].item(),2)
        targ_magH = round(star_table['FLUX_H'][0].item(),2)

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

        print('\nGetting Simbad values for %s:' % star)
        print('Position RA  = %s' % targ_ra)
        print('Position DEC = %s' % targ_dec)
        print('Proper motion RA  = %s as/yr' % targ_pmra)
        print('Proper motion DEC = %s as/yr' % targ_pmdec)
        print('K magnitude = %.2f' % targ_magK)
        print('H magnitude = %.2f' % targ_magH)
        print('V magnitude = %.2f' % targ_magV)

        obId = ob['obId']

        ob['constraints']['skyTransparency'] = 'Clear'

        ob['obsDescription']['name'] = ob_name

        ob['target']['name'] = star
        ob['target']['dec'] = targ_dec
        ob['target']['ra'] = targ_ra
        ob['target']['properMotionDec'] = targ_pmdec
        ob['target']['properMotionRa'] = targ_pmra

        ob, obVersion = api.saveOB(ob, obVersion)

        self.api = api
        self.obId = obId
        self.target = star
        self.targ_ra = targ_ra
        self.targ_dec = targ_dec
        self.targ_pmra = targ_pmra
        self.targ_pmdec = targ_pmdec
        self.targ_magK = targ_magK
        self.targ_magV = targ_magV
        self.targ_magH = targ_magH


        # do the individual templates
        for idx in range(1, len(dictionary), 1):
            templatename = 'template%i' % (idx+1)
            template = dictionary[templatename]
            if template['type'] == 'acquisition':
                self.createACQ(template)
            elif template['type'] == 'dither':
                self.createDITHER(template)
            elif template['type'] == 'observation':
                self.createEXP(template)
            elif template['type'] == 'swap':
                self.createSWAP(template)
            else:
                raise ValueError('Type of %s not known, has to be acquisition, dither or observation' % templatename)

        print('\n\nOB is ceated in P2')


    def createACQ(self, tempdict):
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
        sobj_x = tempdict['RA offset']
        sobj_y = tempdict['DEC offset']

        acqTpl, acqTplVersion  = self.api.setTemplateParams(self.obId, acqTpl, {
            'SEQ.FT.ROBJ.NAME': self.target,
            'SEQ.FT.ROBJ.MAG': self.targ_magK,
            'SEQ.FT.ROBJ.DIAMETER': 0.0,
            'SEQ.FT.ROBJ.VIS': 1.0,
            'SEQ.FT.MODE': 'AUTO',
            'SEQ.INS.SOBJ.NAME': self.target,
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
            'ISS.BASELINE': ['UTs'],
            'ISS.VLTITYPE': ['astrometry'],
        }, acqTplVersion)


    def createDITHER(self, tempdict):
        """
        Create dither template and adds it to OB
        """
        print('Cannot dither, as this is used as an acquisition in P2')
        print('Therefore not able to do this (yet?)')
        print('Gonna abort')
        return None



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
