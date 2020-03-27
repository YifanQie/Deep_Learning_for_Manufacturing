% plot mesh model for selected component
function meshComponentPlot(fem,...
                           idcomp,...
                           tag,...
                           logPanel)

if nargin==2
    tag='';
    logPanel=[];
end

if nargin==3
    logPanel=[];
end

% PLOT TRIA:
nele=length(fem.Domain(idcomp).ElementTria);

tria=zeros(nele,3);
for i=1:nele
      id=fem.Domain(idcomp).ElementTria(i);

          tria(i,:)=fem.xMesh.Element(id).Element;

end

if ~isempty(tria)

    idnode=unique(tria(:));   
    node=fem.xMesh.Node.Coordinate(idnode,:);
    nodenorm=-fem.xMesh.Node.Normal(idnode,:);

    tria=renumberElements(tria, idnode);

    if fem.Post.Options.ShowPatch
        if fem.Post.Options.ShowEdge
            patch('faces',tria,...
                 'vertices',node,...
                 'edgecolor',fem.Post.Options.ColorEdge,...
                 'facecolor',fem.Post.Options.ColorPatch,...
                 'parent',fem.Post.Options.ParentAxes,...
                 'facealpha',fem.Post.Options.FaceAlpha,...
                 'tag',tag,...
                 'buttondownfcn',{@logCurrentSelection, logPanel},...
                 'FaceLighting','phong',...
                 'EdgeLighting','phong',...
                 'VertexNormals',nodenorm)
        else
            patch('faces',tria,...
                 'vertices',node,...
                 'edgecolor','none',...
                 'facecolor',fem.Post.Options.ColorPatch,...
                 'parent',fem.Post.Options.ParentAxes,...
                 'facealpha',fem.Post.Options.FaceAlpha,...
                 'tag',tag,...
                 'buttondownfcn',{@logCurrentSelection, logPanel},...
                 'FaceLighting','phong',...
                 'EdgeLighting','phong',...
                 'VertexNormals',nodenorm)
        end

    else
        if fem.Post.Options.ShowEdge
            patch('faces',tria,...
                 'vertices',node,...
                 'edgecolor',fem.Post.Options.ColorEdge,...
                 'facecolor','none',...
                 'parent',fem.Post.Options.ParentAxes,...
                 'facealpha',fem.Post.Options.FaceAlpha,...
                 'tag',tag,...
                 'buttondownfcn',{@logCurrentSelection, logPanel},...
                 'FaceLighting','phong',...
                 'EdgeLighting','phong',...
                 'VertexNormals',nodenorm)
        else
           patch('faces',tria,...
                 'vertices',node,...
                 'edgecolor','none',...
                 'facecolor','none',...
                 'parent',fem.Post.Options.ParentAxes,...
                 'facealpha',fem.Post.Options.FaceAlpha,...
                 'tag',tag,...
                 'buttondownfcn',{@logCurrentSelection, logPanel},...
                 'FaceLighting','phong',...
                 'EdgeLighting','phong',...
                 'VertexNormals',nodenorm)
        end
    end

end


% PLOT QUAD:
nele=length(fem.Domain(idcomp).ElementQuad);

quad=zeros(nele,4);
for i=1:nele
      id=fem.Domain(idcomp).ElementQuad(i);

          quad(i,:)=fem.xMesh.Element(id).Element;

end

if ~isempty(quad)

    idnode=unique(quad(:));   
    node=fem.xMesh.Node.Coordinate(idnode,:);
    nodenorm=-fem.xMesh.Node.Normal(idnode,:);

    quad=renumberElements(quad, idnode);

    if fem.Post.Options.ShowPatch
        if fem.Post.Options.ShowEdge
            patch('faces',quad,...
                 'vertices',node,...
                 'edgecolor',fem.Post.Options.ColorEdge,...
                 'facecolor',fem.Post.Options.ColorPatch,...
                 'parent',fem.Post.Options.ParentAxes,...
                 'facealpha',fem.Post.Options.FaceAlpha,...
                 'tag',tag,...
                 'buttondownfcn',{@logCurrentSelection, logPanel},...
                 'EdgeLighting','phong',...
                 'FaceLighting','phong',...
                 'VertexNormals',nodenorm)
        else
            patch('faces',quad,...
                 'vertices',node,...
                 'edgecolor','none',...
                 'facecolor',fem.Post.Options.ColorPatch,...
                 'parent',fem.Post.Options.ParentAxes,...
                 'facealpha',fem.Post.Options.FaceAlpha,...
                 'tag',tag,...
                 'buttondownfcn',{@logCurrentSelection, logPanel},...
                 'EdgeLighting','phong',...
                 'FaceLighting','phong',...
                 'VertexNormals',nodenorm)
        end

    else
        if fem.Post.Options.ShowEdge
            patch('faces',quad,...
                 'vertices',node,...
                 'edgecolor',fem.Post.Options.ColorEdge,...
                 'facecolor','none',...
                 'parent',fem.Post.Options.ParentAxes,...
                 'facealpha',fem.Post.Options.FaceAlpha,...
                 'tag',tag,...
                 'buttondownfcn',{@logCurrentSelection, logPanel},...
                 'EdgeLighting','phong',...
                 'FaceLighting','phong',...
                 'VertexNormals',nodenorm)
        else
           patch('faces',quad,...
                 'vertices',node,...
                 'edgecolor','none',...
                 'facecolor','none',...
                 'parent',fem.Post.Options.ParentAxes,...
                 'facealpha',fem.Post.Options.FaceAlpha,...
                 'tag',tag,...
                 'buttondownfcn',{@logCurrentSelection, logPanel},...
                 'EdgeLighting','phong',...
                 'FaceLighting','phong',...
                 'VertexNormals',nodenorm)
        end
    end

end


if fem.Post.Options.ShowAxes
    set(fem.Post.Options.ParentAxes,'visible','on')
else
    set(fem.Post.Options.ParentAxes,'visible','off')
end
