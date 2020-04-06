def get_sample_status(sample):
    """Get the manually defined sample status"""
    #for s in sample_db:
    #    self.man_class_merged[s.sample_ID] = []
    #    self.man_class[s.sample_ID] = {}
    #    for key in ['T13','T18','T21','X0','XXX','XXY','XYY']:
    #        status = s.__dict__['status_'+key]
    #        if status!='Normal':
    #            self.man_class[s.sample_ID][key] = status
    #            self.man_class_merged[s.sample_ID].append(' '.join([status, key]))
    #        else:
    #            self.man_class[s.sample_ID][key] = '-'
    return ['Suspected T18']
    
    
    #manually_classifyed={u'test-2020-07892-06_AHCKMCBCX3': u'Suspected T18', u'test-2020-07887-06_AHCKMCBCX3': '', u'test-2020-07897-06_AHCKMCBCX3': '', u'test-2020-07893-06_AHCKMCBCX3': '', u'test-2020-07890-06_AHCKMCBCX3': '', u'test-2020-07886-06_AHCKMCBCX3': '', u'test-2020-07889-06_AHCKMCBCX3': '', u'test-2020-07910-06_AHCKMCBCX3': '', u'pcs-2020-05298-01_AHCKMCBCX3': '', u'test-2020-07885-06_AHCKMCBCX3': '', u'test-2020-07888-06_AHCKMCBCX3': '', u'test-2020-07884-06_AHCKMCBCX3': '', u'test-2020-07896-06_AHCKMCBCX3': '', u'test-2020-07895-06_AHCKMCBCX3': '', u'test-2020-07894-06_AHCKMCBCX3': ''}


def get_sample_info(sample):
    sample_info = {'FF_Formatted':,
                   'Zscore_13': sample.get('NCV_13'),
                   'Zscore_18': sample.get('NCV_18'),
                   'Zscore_21': sample.get('NCV_21'),
                   'Zscore_X': sample.get('NCV_X'),
                   'Warning': sample.get('NCV_13'),
                   'Status': sample.get('NCV_13'),
                   'Include': sample.get('NCV_13'),
                   'Comment': sample.get('NCV_13'),
                   'Last_Change': sample.get('NCV_13')}




def _get_tris_warn(self):
    """Get automated trisomi warnings, based on preset NCV thresholds"""
    for key in ['13','18','21','X','Y']:
        if self.sample.__dict__['NCV_'+key] in self.exceptions:
            val = self.sample.__dict__['NCV_'+key]
            warn = "default"
        else:
            val = round(float(self.sample.__dict__['NCV_'+key]),2)
            if  key in ['13','18','21']:
                if self.fetal_fraction <= 5:
                    smax = self.tris_thresholds['soft_max_ff']['NCV']
                else:
                    smax = self.tris_thresholds['soft_max']['NCV']
                hmin = self.tris_thresholds['hard_min']['NCV']
                hmax = self.tris_thresholds['hard_max']['NCV']
                smin = self.tris_thresholds['soft_min']['NCV']
                    
                if (smax <= val < hmax) or (hmin < val <= smin):
                    warn = "warning"
                    self.NCV_classified.append('T'+key)
                elif (val >= hmax) or (val <= hmin):
                    warn = "danger"
                    self.NCV_classified.append('T'+key)
                else:
                    warn = "default"
        self.NCV_data['NCV_'+key] = {'val': val, 'warn': warn }


def _get_FF_warning(self):
    self.NCV_data['FF_Formatted'] = {}
    try:
        self.fetal_fraction = float(self.sample.sample.FF_Formatted.rstrip('%').lstrip('<'))
    except:
        self.fetal_fraction = None
    if self.fetal_fraction:
        self.NCV_data['FF_Formatted']['val'] = self.fetal_fraction
        if self.fetal_fraction <= self.ff_treshold:
            self.NCV_classified.append('low FF')
            self.NCV_data['FF_Formatted']['warn'] = "danger"
        else:
            self.NCV_data['FF_Formatted']['warn'] = "default"

#NCV_classified={u'test-2020-07892-06_AHCKMCBCX3': 'T18', u'test-2020-07887-06_AHCKMCBCX3': '', u'test-2020-07897-06_AHCKMCBCX3': '', u'test-2020-07893-06_AHCKMCBCX3': '', u'test-2020-07890-06_AHCKMCBCX3': '', u'test-2020-07886-06_AHCKMCBCX3': '', u'test-2020-07889-06_AHCKMCBCX3': '', u'test-2020-07910-06_AHCKMCBCX3': '', u'pcs-2020-05298-01_AHCKMCBCX3': '', u'test-2020-07885-06_AHCKMCBCX3': '', u'test-2020-07888-06_AHCKMCBCX3': '', u'test-2020-07884-06_AHCKMCBCX3': '', u'test-2020-07896-06_AHCKMCBCX3': '', u'test-2020-07895-06_AHCKMCBCX3': '', u'test-2020-07894-06_AHCKMCBCX3': ''}


#NCV_data={u'test-2020-07892-06_AHCKMCBCX3': {'FF_Formatted': {'warn': 'default', 'val': 4.0}, 'NCV_Y': {'warn': 'default', 'val': -0.54}, 'NCV_X': {'warn': 'default', 'val': 2.09}, 'NCV_21': {'warn': 'default', 'val': -0.12}, 'NCV_13': {'warn': 'default', 'val': -1.09}, 'NCV_18': {'warn': 'danger', 'val': 11.44}}, u'test-2020-07887-06_AHCKMCBCX3': {'FF_Formatted': {'warn': 'default', 'val': 8.0}, 'NCV_Y': {'warn': 'default', 'val': -0.57}, 'NCV_X': {'warn': 'default', 'val': -0.94}, 'NCV_21': {'warn': 'default', 'val': 0.03}, 'NCV_13': {'warn': 'default', 'val': 0.61}, 'NCV_18': {'warn': 'default', 'val': -0.35}}, u'test-2020-07897-06_AHCKMCBCX3': {'FF_Formatted': {'warn': 'default', 'val': 9.0}, 'NCV_Y': {'warn': 'default', 'val': 219.09}, 'NCV_X': {'warn': 'default', 'val': -10.79}, 'NCV_21': {'warn': 'default', 'val': -0.11}, 'NCV_13': {'warn': 'default', 'val': 0.05}, 'NCV_18': {'warn': 'default', 'val': 1.38}}, u'test-2020-07893-06_AHCKMCBCX3': {'FF_Formatted': {'warn': 'default', 'val': 10.0}, 'NCV_Y': {'warn': 'default', 'val': 0.02}, 'NCV_X': {'warn': 'default', 'val': 0.17}, 'NCV_21': {'warn': 'default', 'val': -0.58}, 'NCV_13': {'warn': 'default', 'val': -0.84}, 'NCV_18': {'warn': 'default', 'val': 0.41}}, u'test-2020-07890-06_AHCKMCBCX3': {'FF_Formatted': {'warn': 'default', 'val': 9.0}, 'NCV_Y': {'warn': 'default', 'val': 1.56}, 'NCV_X': {'warn': 'default', 'val': -1.64}, 'NCV_21': {'warn': 'default', 'val': -0.02}, 'NCV_13': {'warn': 'default', 'val': -1.95}, 'NCV_18': {'warn': 'default', 'val': -0.0}}, u'test-2020-07886-06_AHCKMCBCX3': {'FF_Formatted': {'warn': 'default', 'val': 10.0}, 'NCV_Y': {'warn': 'default', 'val': -0.77}, 'NCV_X': {'warn': 'default', 'val': 0.67}, 'NCV_21': {'warn': 'default', 'val': 0.61}, 'NCV_13': {'warn': 'default', 'val': -0.32}, 'NCV_18': {'warn': 'default', 'val': 0.27}}, u'test-2020-07889-06_AHCKMCBCX3': {'FF_Formatted': {'warn': 'default', 'val': 8.0}, 'NCV_Y': {'warn': 'default', 'val': 0.64}, 'NCV_X': {'warn': 'default', 'val': -0.33}, 'NCV_21': {'warn': 'default', 'val': 0.55}, 'NCV_13': {'warn': 'default', 'val': -0.52}, 'NCV_18': {'warn': 'default', 'val': -0.23}}, u'test-2020-07910-06_AHCKMCBCX3': {'FF_Formatted': {'warn': 'default', 'val': 8.0}, 'NCV_Y': {'warn': 'default', 'val': 0.49}, 'NCV_X': {'warn': 'default', 'val': 0.47}, 'NCV_21': {'warn': 'default', 'val': -0.58}, 'NCV_13': {'warn': 'default', 'val': -0.23}, 'NCV_18': {'warn': 'default', 'val': 0.95}}, u'pcs-2020-05298-01_AHCKMCBCX3': {'FF_Formatted': {'warn': 'default', 'val': 8.0}, 'NCV_Y': {'warn': 'default', 'val': 64.46}, 'NCV_X': {'warn': 'default', 'val': -3.78}, 'NCV_21': {'warn': 'default', 'val': 0.7}, 'NCV_13': {'warn': 'default', 'val': -0.89}, 'NCV_18': {'warn': 'default', 'val': 0.46}}, u'test-2020-07885-06_AHCKMCBCX3': {'FF_Formatted': {'warn': 'default', 'val': 9.0}, 'NCV_Y': {'warn': 'default', 'val': 2.02}, 'NCV_X': {'warn': 'default', 'val': 1.4}, 'NCV_21': {'warn': 'default', 'val': 0.61}, 'NCV_13': {'warn': 'default', 'val': 0.11}, 'NCV_18': {'warn': 'default', 'val': 0.59}}, u'test-2020-07888-06_AHCKMCBCX3': {'FF_Formatted': {'warn': 'default', 'val': 12.0}, 'NCV_Y': {'warn': 'default', 'val': 169.68}, 'NCV_X': {'warn': 'default', 'val': -10.82}, 'NCV_21': {'warn': 'default', 'val': 0.04}, 'NCV_13': {'warn': 'default', 'val': -0.5}, 'NCV_18': {'warn': 'default', 'val': -0.42}}, u'test-2020-07884-06_AHCKMCBCX3': {'FF_Formatted': {'warn': 'default', 'val': 7.0}, 'NCV_Y': {'warn': 'default', 'val': 116.61}, 'NCV_X': {'warn': 'default', 'val': -7.22}, 'NCV_21': {'warn': 'default', 'val': 0.11}, 'NCV_13': {'warn': 'default', 'val': 0.78}, 'NCV_18': {'warn': 'default', 'val': 0.75}}, u'test-2020-07896-06_AHCKMCBCX3': {'FF_Formatted': {'warn': 'default', 'val': 4.0}, 'NCV_Y': {'warn': 'default', 'val': 78.66}, 'NCV_X': {'warn': 'default', 'val': -3.38}, 'NCV_21': {'warn': 'default', 'val': 0.58}, 'NCV_13': {'warn': 'default', 'val': -1.36}, 'NCV_18': {'warn': 'default', 'val': -0.34}}, u'test-2020-07895-06_AHCKMCBCX3': {'FF_Formatted': {'warn': 'default', 'val': 9.0}, 'NCV_Y': {'warn': 'default', 'val': -0.56}, 'NCV_X': {'warn': 'default', 'val': -1.12}, 'NCV_21': {'warn': 'default', 'val': -0.76}, 'NCV_13': {'warn': 'default', 'val': -0.06}, 'NCV_18': {'warn': 'default', 'val': -0.63}}, u'test-2020-07894-06_AHCKMCBCX3': {'FF_Formatted': {'warn': 'default', 'val': 8.0}, 'NCV_Y': {'warn': 'default', 'val': 114.35}, 'NCV_X': {'warn': 'default', 'val': -8.11}, 'NCV_21': {'warn': 'default', 'val': 0.0}, 'NCV_13': {'warn': 'default', 'val': 0.25}, 'NCV_18': {'warn': 'default', 'val': -1.57}}}