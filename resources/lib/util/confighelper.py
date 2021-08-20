import configparser
import os
import xbmcaddon


class ConfigHelper:
    config_path = None
    addon_path = None
    binary_path = None
    launchscripts_path = None
    logger = None
    plugin = None
    config = {
        'host_addr':                    None,
        'resolution_width':             None,
        'resolution_height':            None,
        'resolution':                   None,
        'framerate':                    None,
        'graphics_optimizations':       None,
        'remote_optimizations':         None,
        'bitrate':                      None,
        'packetsize':                   None,
        'audio_device':                 None,
        'audio_device_parameter':       None,
        'local_audio':                  None,
        'debug_mode':                   None,
        'codec':                        None,
        'surround':                     None,
        'nounsupported_flag':           None,
    }

    def __init__(self, plugin, logger):
        self.plugin = plugin
        self.addon_path = xbmcaddon.Addon().getAddonInfo('path')
        self.logger = logger
        self._reset()
        self.configure(False)


    def _reset(self):
        for elem in self.config:
            self.config[elem] = None

    def configure(self, dump=True):
        self.binary_path = self._find_binary(self.addon_path)

        if self.binary_path is None:
            self.logger.info('Moonlight binary could not be found. Configuration file saved at %s' % self.addon_path)
            self.config_path = self.addon_path + 'moonlight.conf'
        else:
            self.config_path = self.binary_path + 'moonlight.conf'

        launchscript_name = self.plugin.getSetting('launchscript_conf')
        if launchscript_name:
            self.launchscripts_path = self.addon_path + 'resources/launchscripts/' + launchscript_name + '/'

        self.config = {
            'host_addr':                    self.plugin.getSetting('host_addr'),
            'resolution':                   self.plugin.getSetting('resolution'),
            'resolution_width':             self.plugin.getSetting('resolution_width'),
            'resolution_height':            self.plugin.getSetting('resolution_height'),
            'codec':                        self.plugin.getSetting('codec'),
            'bitrate':                      self.plugin.getSettingInt('bitrate'),
            'framerate':                    self.plugin.getSetting('framerate'),
            'surround':                     self.plugin.getSetting('surround'),
            'audio_device':                 self.plugin.getSetting('audio_device'),
            'audio_device_parameter':       self.plugin.getSetting('audio_device_parameter'),
            'packetsize':                   self.plugin.getSettingInt('packetsize'),
            'nounsupported_flag':           self.plugin.getSetting('nounsupported_flag'),
            'nomouseemulation_flag':        self.plugin.getSetting('nomouseemulation_flag'),
            'graphics_optimizations':       self.plugin.getSetting('graphic_optimizations'),
            'remote_optimizations':         self.plugin.getSetting('remote_optimizations'),
            'local_audio':                  self.plugin.getSetting('local_audio'),
            'debug_mode':                   self.plugin.getSetting('debug_mode'),
        }

        if dump:
            self._dump_conf()

    def _dump_conf(self):
        """
        This dumps the currently configured helper into a file moonlight can read
        """
        config = configparser.ConfigParser()
        config.read(self.config_path)

        if 'Moonlight' not in config.sections():
            config.add_section('Moonlight')

        if self.config['host_addr']:
            config.set('Moonlight', 'address', self.config['host_addr'])
        else:
            config.remove_option('Moonlight', 'address')
        
        resolution_width = '1280'
        resolution_height = '720'
        if self.config['resolution'] == 'Custom':
            resolution_width = self.config['resolution_width']
            resolution_height = self.config['resolution_height']
        else:
            res = self.config['resolution'].split('x')
            resolution_width = res[0]
            resolution_height = res[1]

        config.set('Moonlight', 'width', resolution_width)
        config.set('Moonlight', 'height', resolution_height)
        
        
        config.set('Moonlight', 'fps', self.config['framerate'])

        config.set('Moonlight', 'bitrate', str(self.config['bitrate'] * 1000))
        config.set('Moonlight', 'packetsize', str(self.config['packetsize']))
        config.set('Moonlight', 'sops', self.config['graphics_optimizations'])
        config.set('Moonlight', 'remote', self.config['remote_optimizations'])
        config.set('Moonlight', 'localaudio', self.config['local_audio'])
        config.set('Moonlight', 'debug', self.config['debug_mode'])
        
        if self.config['local_audio'] == 'true':
            config.remove_option('Moonlight', 'audio')
        else:
            if self.config['audio_device_parameter']:
                config.set('Moonlight', 'audio', self.config['audio_device_parameter'])
            else:
                config.set('Moonlight', 'audio', self.config['audio_device'])

        config.set('Moonlight', 'codec', self.config['codec'])
        if self.config['surround'] != 'false':
            config.set('Moonlight', 'surround', self.config['surround'])
        else:
            config.remove_option('Moonlight', 'surround')
        
        config.set('Moonlight', 'nounsupported', self.config['nounsupported_flag'])
        config.set('Moonlight', 'nomouseemulation', self.config['nomouseemulation_flag'])

        with open(self.config_path, 'w') as configfile:
            config.write(configfile)
        configfile.close()

        self.logger.info('[ConfigHelper] - Dumped config to disk.')

    @staticmethod
    def _find_binary(internal_path):
        binary_locations = [
            '/usr/bin/moonlight',
            '/usr/local/bin/moonlight',
            '/storage/moonlight/moonlight',
            os.path.join(internal_path, 'bin', 'moonlight')
        ]

        for f in binary_locations:
            if os.path.isfile(f):
                return os.path.dirname(f) + '/'

        return None