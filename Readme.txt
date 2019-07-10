How to use:

Download the folder Executbale Version. Edit the config.txt folder. Double click run.exe.

1. configure script using config.txt
    - root means the location of your library

        example:

        root;C:/Users/Administrator/Music

    - location means where you are

        example:

        location;us
        ^this means you are in the united states

        see bottom for the country code list

    - resolution means how big your image is

        example:

        resolution;600
        ^ this means it will be a 600x600 square

        resolution;default
        ^this means it will use the biggest available image

    - extensions means what extensions will be considered Music

        example:

        extensions;mp3,flac
        ^this means that flac and mp3 files will be considered song files

        Other extensions MAY OR MAY NOT WORK depending on how they store the metadata
        
        
        
###################################################################################################################
###################################################################################################################
###                             IF YOU ARE USING THE EXECUTABLE VERSION, IGNORE BELOW                           ###        
###################################################################################################################
###################################################################################################################





2. Install dependencies
    This python script requires some external tools to help it run 

    double-click install.bat
        In case you were wondering what this does, it installs pip, a tool that assists installation of other tools
        It then uses pip to install the following dependencies:
            requests
            json
            mutagen
            math
            PIL
    
3. Run program
    
    double-click run.bat
        This batch file will then open run.py which uses albumGrabberOOP.py
    
    Wait for it to go through your entire library and find images online. Will take approximately 3 seconds per album in the library
    
    Afterwards, it will allow you to pick from a list of possible albums. This is because there could be some differences in naming,
    for example, blink-182 and Blink - 182

    Sometimes it will be unable to find a song. That is okay, you can manually search for it using the included functionality

    At the end, it will download and save all the songs as folder.jpg. 

4. Attach image to songs

    If you would like your image to be attached to the song, you can use tools such as:
        Album Cover Applier
        Tag&Rename
    These are both tools that are capable of embedding the image into the actual music file.

For country: 
ae: 'United Arab Emirates',
ag: 'Antigua and Barbuda',
ai: 'Anguilla',
al: 'Albania',
am: 'Armenia',
ao: 'Angola',
ar: 'Argentina',
at: 'Austria',
au: 'Australia',
az: 'Azerbaijan',
bb: 'Barbados',
be: 'Belgium',
bf: 'Burkina-Faso',
bg: 'Bulgaria',
bh: 'Bahrain',
bj: 'Benin',
bm: 'Bermuda',
bn: 'Brunei Darussalam',
bo: 'Bolivia',
br: 'Brazil',
bs: 'Bahamas',
bt: 'Bhutan',
bw: 'Botswana',
by: 'Belarus',
bz: 'Belize',
ca: 'Canada',
cg: 'Democratic Republic of the Congo',
ch: 'Switzerland',
cl: 'Chile',
cn: 'China',
co: 'Colombia',
cr: 'Costa Rica',
cv: 'Cape Verde',
cy: 'Cyprus',
cz: 'Czech Republic',
de: 'Germany',
dk: 'Denmark',
dm: 'Dominica',
do: 'Dominican Republic',
dz: 'Algeria',
ec: 'Ecuador',
ee: 'Estonia',
eg: 'Egypt',
es: 'Spain',
fi: 'Finland',
fj: 'Fiji',
fm: 'Federated States of Micronesia',
fr: 'France',
gb: 'Great Britain',
gd: 'Grenada',
gh: 'Ghana',
gm: 'Gambia',
gr: 'Greece',
gt: 'Guatemala',
gw: 'Guinea Bissau',
gy: 'Guyana',
hk: 'Hong Kong',
hn: 'Honduras',
hr: 'Croatia',
hu: 'Hungaria',
id: 'Indonesia',
ie: 'Ireland',
il: 'Israel',
in: 'India',
is: 'Iceland',
it: 'Italy',
jm: 'Jamaica',
jo: 'Jordan',
jp: 'Japan',
ke: 'Kenya',
kg: 'Krygyzstan',
kh: 'Cambodia',
kn: 'Saint Kitts and Nevis',
kr: 'South Korea',
kw: 'Kuwait',
ky: 'Cayman Islands',
kz: 'Kazakhstan',
la: 'Laos',
lb: 'Lebanon',
lc: 'Saint Lucia',
lk: 'Sri Lanka',
lr: 'Liberia',
lt: 'Lithuania',
lu: 'Luxembourg',
lv: 'Latvia',
md: 'Moldova',
mg: 'Madagascar',
mk: 'Macedonia',
ml: 'Mali',
mn: 'Mongolia',
mo: 'Macau',
mr: 'Mauritania',
ms: 'Montserrat',
mt: 'Malta',
mu: 'Mauritius',
mw: 'Malawi',
mx: 'Mexico',
my: 'Malaysia',
mz: 'Mozambique',
na: 'Namibia',
ne: 'Niger',
ng: 'Nigeria',
ni: 'Nicaragua',
nl: 'Netherlands',
np: 'Nepal',
no: 'Norway',
nz: 'New Zealand',
om: 'Oman',
pa: 'Panama',
pe: 'Peru',
pg: 'Papua New Guinea',
ph: 'Philippines',
pk: 'Pakistan',
pl: 'Poland',
pt: 'Portugal',
pw: 'Palau',
py: 'Paraguay',
qa: 'Qatar',
ro: 'Romania',
ru: 'Russia',
sa: 'Saudi Arabia',
sb: 'Soloman Islands',
sc: 'Seychelles',
se: 'Sweden',
sg: 'Singapore',
si: 'Slovenia',
sk: 'Slovakia',
sl: 'Sierra Leone',
sn: 'Senegal',
sr: 'Suriname',
st: 'Sao Tome e Principe',
sv: 'El Salvador',
sz: 'Swaziland',
tc: 'Turks and Caicos Islands',
td: 'Chad',
th: 'Thailand',
tj: 'Tajikistan',
tm: 'Turkmenistan',
tn: 'Tunisia',
tr: 'Turkey',
tt: 'Republic of Trinidad and Tobago',
tw: 'Taiwan',
tz: 'Tanzania',
ua: 'Ukraine',
ug: 'Uganda',
us: 'United States of America',
uy: 'Uruguay',
uz: 'Uzbekistan',
vc: 'Saint Vincent and the Grenadines',
ve: 'Venezuela',
vg: 'British Virgin Islands',
vn: 'Vietnam',
ye: 'Yemen',
za: 'South Africa',
zw: 'Zimbabwe'



