function [status] = scene_merge_v2(ffmpeg_bin)
% 
% Scene cut-transcode-merge utility function
% [status] = scene_ctm_v1(vid_in,vid_out,max_chunks,thres)
% Parameters:
% ffmpeg_bin:           the binary of ffmpeg
%

status=-1; % by default return error code -1 if function does not complete

% create output folder/clean it up
mkdir('./output'); 
delete('./output/*.*'); delete('./output/*');

% get all directories
dir_input = dir('./input/*');
if length(dir_input)==0 
    fprintf('\nerror: ./input folder non-existent or no directories found within.\n\n');
    return;
end


for ind_vid=1:length(dir_input)
    
	vid_in = ['./input/' dir_input(ind_vid).name];
    ind_prefix_pos=strfind(lower(vid_in),'seg0_')+5;
    vid_in_name=vid_in(ind_prefix_pos:end);

    % find out how many segments do we have 
    tot_segs=length(dir(['./input/*' vid_in_name]));
    if tot_segs<1
        fprintf('\nUnexpected error: found %d segments for file %s.\n\n',tot_segs,vid_in_name);
        return;
    else
        fprintf('\nFound %d segments of video %s, merging them...',tot_segs,vid_in_name);
    end
    for curr_seg=0:tot_segs-1
        fin_test=fopen(['./input/' vid_in_name '/SEG' num2str(curr_seg) '_' vid_in_name '.mp4'],'rb');
        if fin_test==-1
            fprintf('\nerror: input video %s was not found.\n\n',['./input/SEG' num2str(curr_seg) '_' vid_in_name '.mp4']);
            return;
        end
        fclose(fin_test);
    end    

    str_all_segs='intermediate0.ts';
    for i=1:tot_segs
        str_transport=[ffmpeg_bin ' -i ./input/"' vid_in_name '"/"SEG' num2str(i-1) '_' vid_in_name '.mp4" -y -c copy -bsf:v h264_mp4toannexb -f mpegts intermediate' num2str(i-1) '.ts'];
        [s w]=dos(str_transport); 
        if i>1
            str_all_segs=[str_all_segs '|intermediate' num2str(i-1) '.ts']; 
        end
    end
    str_concat=[ffmpeg_bin ' -i "concat:' str_all_segs '" -y -c copy -bsf:a aac_adtstoasc -movflags +faststart ./output/"' vid_in_name '.mp4"'];
    [s w]=dos(str_concat); 

    % cleanup
    % delete tmp txt chunks files
    delete('intermediate*.*');
    fprintf('\tdone.');
end


fprintf('\n\n');

status=0;
return;

