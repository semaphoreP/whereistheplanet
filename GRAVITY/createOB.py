from datetime import datetime


class CreateOB():    
    def __init__(self, dictionary):
        """
        Create an OB for exoplanet observation with GRAVITY
        Input has to be a dictionary 
        """
        self.name_ft = "NAME"
        self.mag_ft = 10.
        
        
        header = dictionary['template1']
        if header['type'] != 'header':
            raise ValueError('First template in file %s has to be a header template'
                             % filename)
        
        obname = header['OB name']
        programID = header['run ID']
        
        self.filename = "OBs/" + obname + '.obd'
        ob = open(self.filename,'w') 
        
        # Create Header
        ob.write('# OB for planet observation \n')
        now = datetime.now()
        now_string = now.strftime('%d-%m-%YT%H:%M:%S')
        ob.write('# Create by createOB at %s\n' % now_string)
        
        ob.write('\n')
        ob.write('# Standard parameter file header\n')
        ob.write('PAF.HDR.START             ;           # Marks start of header\n')
        ob.write('PAF.TYPE                "OB Description";  # Type of parfile\n')
        ob.write('PAF.ID                  "";     # Unused\n')
        ob.write('PAF.NAME                "";     # Unused\n')
        ob.write('PAF.DESC                "";     # Unused\n')
        ob.write('PAF.CRTE.NAME        "BOB";     # Broker for OBs\n')
        ob.write('PAF.CRTE.DAYTIM     "%s"; # Date+time of creation\n' % now_string)
        ob.write('PAF.LCHG.NAME           "";     # Unused\n')
        ob.write('PAF.LCHG.DAYTIM     "%s"; # Date+time of last change\n' % now_string)
        ob.write('PAF.CHCK.NAME           "";     # Unused\n')
        ob.write('PAF.CHCK.DAYTIM         "";     # Unused\n')
        ob.write('PAF.CHCK.CHECKSUM       "";     # Unused\n')
        ob.write('PAF.HDR.END               ;       # Marks end of header\n')
        ob.write('\n')
        ob.write('# Observation Block description follows\n')
        ob.write('OBS.ID                         "2229478"\n')
        ob.write('OBS.DID                        "ESO-VLT-DIC.OBS-2.0"\n')
        ob.write('OBS.GRP                        "0"\n')
        ob.write('OBS.NAME                       "SCIENCE"\n')
        ob.write('OBS.PI-COI.ID                  "0"\n')
        ob.write('OBS.PI-COI.NAME                "EXOGRAV"\n')
        ob.write('OBS.PROG.ID                    "%s"\n' % programID)
        ob.write('\n')
        ob.close()
        
        for idx in range(1, len(dictionary), 1):
            templatename = 'template%i' % (idx+1)
            template = dictionary[templatename]
            if template['type'] == 'acquisition':
                self.createACQ(template)
            elif template['type'] == 'dither':
                self.createDITHER(template)
            elif template['type'] == 'observation':
                self.createEXP(template)
            else:
                raise ValueError('Type of %s not known, has to be acquisition, dither or observation' % templatename)



    def createACQ(self, tempdict):
        """
        Create aquisition template and adds it to OB
        """
        name_sc = tempdict['target name']
        name_ft = name_sc
        targ_ra = tempdict['RA'].replace(":", "")
        targ_dec = tempdict['DEC'].replace(":", "")
        targ_pma = tempdict['pmRA']/1000
        targ_pmd = tempdict['pmDEC']/1000
        mag_sc = tempdict['K mag']
        mag_ft = mag_sc
        mag_h = tempdict['H mag']
        resolution = tempdict['resolution']
        wollaston = tempdict['wollaston']
        mag_cou = tempdict['GS mag']
        sobj_x = tempdict['RA offset']
        sobj_y = tempdict['DEC offset']
        self.name_ft = name_ft
        self.mag_ft = mag_ft
        
        ob = open(self.filename,'a') 
        ob.write('# Acquisition \n')
        ob.write('TPL.ID                         "GRAVITY_dual_acq"\n')
        ob.write('TPL.NAME                       "ACQUISITION FT:%s, SC:%s"\n' % (name_ft, name_sc))
        ob.write('TPL.NEXP                       "1"\n')
        ob.write('TPL.MODE                       "ACQUISITION"\n')
        ob.write('DET1.DIT                       "0.7"\n')
        ob.write('DET2.DIT                       "0.3"\n')
        ob.write('DET2.NDIT.SKY                  "1"\n')
        ob.write('INS.FT.POL                     "%s"\n' % wollaston)
        ob.write('INS.SPEC.POL                   "%s"\n' % wollaston)
        ob.write('INS.SPEC.RES                   "%s"\n' % resolution)
        ob.write('INS.STSOFFANG                  "90.0"\n')
        ob.write('\n')
        ob.write('# AO guide star\n')
        ob.write('COU.AG.ALPHA                   "00:00:00.000"\n')
        ob.write('COU.AG.DELTA                   "00:00:00.000"\n')
        ob.write('COU.AG.GSSOURCE                "SCIENCE"\n')
        ob.write('COU.AG.PMA                     "0.0"\n')
        ob.write('COU.AG.PMD                     "0.0"\n')
        ob.write('COU.AG.TYPE                    "ADAPT_OPT"\n')
        ob.write('COU.GS.FWHM                    "0."\n')
        ob.write('COU.GS.MAG                     "%f"\n' % mag_cou)
        ob.write('\n')
        ob.write('SEQ.FI.HMAG                    "%f"\n' % mag_h)
        ob.write('SEQ.FI.WIN                     "30"\n')
        ob.write('SEQ.FT.ROBJ.DIAMETER           "0.0"\n')
        ob.write('SEQ.FT.ROBJ.VIS                "1.0"\n')
        ob.write('SEQ.FT.ROBJ.MAG                "%f"\n' % mag_ft)
        ob.write('SEQ.FT.ROBJ.NAME               "%s"\n' % name_ft)
        ob.write('SEQ.FT.MODE                    "AUTO"\n')
        ob.write('SEQ.INS.SOBJ.DIAMETER          "0.0"\n')
        ob.write('SEQ.INS.SOBJ.MAG               "%f"\n' % mag_sc)
        ob.write('SEQ.INS.SOBJ.NAME              "%s"\n' % name_sc)
        ob.write('SEQ.INS.SOBJ.VIS               "1.0"\n')
        ob.write('SEQ.INS.SOBJ.PMA               "0"\n')
        ob.write('SEQ.INS.SOBJ.PMD               "0"\n')
        ob.write('SEQ.INS.SOBJ.RADVEL            "0"\n')
        ob.write('SEQ.INS.SOBJ.X                 "%f"\n' % sobj_x)
        ob.write('SEQ.INS.SOBJ.Y                 "%f"\n' % sobj_y)
        ob.write('SEQ.PICKSC                     "F"\n')
        ob.write('SEQ.SKY.X                      "2000"\n')
        ob.write('SEQ.SKY.Y                      "2000"\n')
        ob.write('SEQ.ALIGN                      "F"\n')
        ob.write('SEQ.FRINGETRACK                "T"\n')
        ob.write('SEQ.PICKFT                     "F"\n')
        ob.write('SEQ.PRESET                     "T"\n')
        ob.write('SEQ.TAKESKY                    "T"\n')
        ob.write('SEQ.TRACKFI                    "T"\n')
        ob.write('SEQ.TRACKPUP                   "T"\n')
        ob.write('SEQ.TRACKROT                   "T"\n')
        ob.write('SEQ.TRACKSC                    "T"\n')
        ob.write('DEL.REF.MODE                   "AUTO"\n')
        ob.write('DEL.REF.NAME                   "1"\n')
        ob.write('DEL.REF.OPL                    "250"\n')
        ob.write('TEL.TARG.ALPHA                 "%s"\n' % targ_ra)
        ob.write('TEL.TARG.DELTA                 "%s"\n' % targ_dec)
        ob.write('TEL.TARG.PMA                   "%s"\n' % targ_pma)
        ob.write('TEL.TARG.PMD                   "%s"\n' % targ_pmd)
        ob.write('TEL.TARG.RADVEL                "0"\n')
        ob.write('TEL.TARG.WLENGTH               "2200"\n')
        ob.write('# epoch 2000.0\n')
        ob.write('\n')
        ob.close()
        
        
    def createDITHER(self, tempdict):
        """
        Create dither template and adds it to OB
        """
        name_sc = tempdict['name science']
        name_ft = self.name_ft
        sobj_x = tempdict['RA offset']
        sobj_y = tempdict['DEC offset']
        mag_ft = self.mag_ft
        mag_sc = tempdict['mag science']
        
        ob = open(self.filename,'a') 
        ob.write('# Dither\n')
        ob.write('TPL.ID                         "GRAVITY_dual_acq_dither"\n')
        ob.write('TPL.NAME                       "DITHER: FT:%s,SC:%s"\n' % (name_ft, name_sc))
        ob.write('DET1.DIT                       "0.7"\n')
        ob.write('SEQ.FT.ROBJ.NAME               "%s"\n' % name_ft)
        ob.write('SEQ.INS.SOBJ.NAME              "%s"\n' % name_sc)
        ob.write('SEQ.INS.SOBJ.X                 "%f"\n' % sobj_x)
        ob.write('SEQ.INS.SOBJ.Y                 "%f"\n' % sobj_y)
        ob.write('SEQ.FT.ROBJ.MAG                "%f"\n' % mag_ft)
        ob.write('SEQ.INS.SOBJ.MAG               "%f"\n' % mag_ft)
        ob.write('SEQ.PICKSC                     "F"\n')
        ob.write('SEQ.PICKFT                     "F"\n')
        ob.write('SEQ.TAKESKY                    "F"\n')
        ob.write('SEQ.FI.WIN                     "30"\n')
        ob.write('SEQ.DITHER.X                   "0"\n')
        ob.write('SEQ.DITHER.Y                   "0"\n')
        ob.write('SEQ.SKY.X                      "2000"\n')
        ob.write('SEQ.SKY.Y                      "2000"\n')
        ob.write('\n')
        ob.close()

        


        
    def createEXP(self, tempdict):
        """
        Create exposure template and adds it to OB
        """
        name_sc = tempdict['name science']
        reloff_x = tempdict['RA offset']
        reloff_y = tempdict['DEC offset']
        dit = tempdict['DIT']
        ndit = tempdict['NDIT']
        sequence = tempdict['sequence']
        
        ob = open(self.filename,'a') 
        ob.write('# Exposure \n')
        ob.write('TPL.ID                         "GRAVITY_dual_obs_exp"\n')
        ob.write('TPL.NAME                       "EXPOSURE SC:%s"\n' % name_sc)
        ob.write('DET1.DIT                       "0.7"\n')
        ob.write('DET1.NDIT                      "0"\n')
        ob.write('DET2.DIT                       "%f"\n' % dit)
        ob.write('DET2.NDIT.OBJECT               "%i"\n' % ndit)
        ob.write('DET2.NDIT.SKY                  "%i"\n' % ndit)
        ob.write('INS.SPEC.POL                   "SAME"\n')
        ob.write('INS.SPEC.RES                   "SAME"\n')
        ob.write('SEQ.OBSSEQ                     "%s"\n' % sequence)
        ob.write('SEQ.HWPOFF                     "0.0"\n')
        ob.write('SEQ.RELOFF.X                   "%f"\n' % reloff_x)
        ob.write('SEQ.RELOFF.Y                   "%f"\n' % reloff_y)
        ob.write('SEQ.SKY.X                      "2000"\n')
        ob.write('SEQ.SKY.Y                      "2000"\n')
        ob.write('\n')
        ob.close()


        
        
    
    
    
    
    
    
