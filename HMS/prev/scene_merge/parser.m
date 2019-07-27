function [status,ffmpeg_bin,ffprobe_bin,threshold_scene,max_chunks,profile_string]=...
    parser(params_txt)

status=-1;
ffmpeg_bin=[];
ffprobe_bin=[];
threshold_scene=[];
max_chunks=[];
profile_string=[];


fin=fopen(params_txt,'rt');
if fin<0
    fprintf('\n\nError: %s file not found',params_txt);
    return;
end
while 1
    next_line=fgetl(fin);
    if next_line==-1
        break;
    end
    if ~isempty(regexp(next_line,'%\sffmpeg_bin'))
        ffmpeg_bin=fgetl(fin);
    elseif ~isempty(regexp(next_line,'%\sffprobe_bin'))
        ffprobe_bin=fgetl(fin);
    elseif ~isempty(regexp(next_line,'%\sthreshold_scene'))
        threshold_scene=str2num(fgetl(fin));
    elseif ~isempty(regexp(next_line,'%\smax_chunks'))
        max_chunks=str2num(fgetl(fin));
    elseif ~isempty(regexp(next_line,'%\sprofile_string'))
        profile_string={}; i=1;
        while 1
            str_in=fgetl(fin);
            if isempty(regexp(str_in,'///prof///'))
                break;
            else
                pos_start=strfind(str_in,'///prof///')+10;
                profile_string(i)={str_in(pos_start:end)};
                i=i+1;
            end
        end
    else
        % ignore
    end
        
        
end
fclose(fin);

if isempty(ffmpeg_bin) || isempty(ffprobe_bin) || isempty(threshold_scene) || isempty(max_chunks) || isempty(profile_string)
    fprintf('\n\nError: One or more of the necessary parameters was not found in file %s\n\n',params_txt);
end

status=0;
return;
