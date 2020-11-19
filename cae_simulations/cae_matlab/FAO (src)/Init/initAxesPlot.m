% Init figure and axes options
function data=initAxesPlot(haxes3d)

data.Axes=haxes3d;

data.Options.ShowAxes=true;
data.Options.Color='w';
data.Options.FontSize=12;
data.Options.SymbolSize=10.0; % symbol size
data.Options.LengthAxis=50.0; % length of axis
data.Options.SubSampling=0.01; % between [0, 1]
data.Options.SearchDistance=10.0; % normal searching distance
data.Options.Renderer={2,'zbuffer','opengl'}; % openGL is preselected
data.Options.SpeedCameraMotion=0.0003; %--
data.Options.Tag.Model='model';
data.Options.Tag.TempObject='tempObj';
data.Options.Tag.TempProbe='tempProbe';
data.Selection=[];


