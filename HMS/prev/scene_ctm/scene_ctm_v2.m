function [status] = scene_ctm_v2(ffmpeg_bin,profile_pass_str)
% 
% Scene cut-transcode-merge utility function
% [status] = scene_ctm_v2(ffmpeg_bin,profile_pass_str)
% Parameters:
% ffmpeg_bin:           the binary of ffmpeg
% profile_pass_str:     single-pass or multi-pass FFMPEG profile string,
%                       e.g., 
%                       {'-c:v libx264 -b:v 800k m 1 -pass 1 -an -f mp4 -y',
%                       '-c:v libx264 -b:v 800k -pass 2 -filter:a pan=stereo:c0=c0:c1=c1 
%                        -c:a libfdk_aac -vbr 5 -f mp4 -movflags +faststart -y'}
%

status=-1; % by default return error code -1 if function does not complete

tot_passes=length(profile_pass_str);
% create output folder/clean it up
mkdir('./output'); 
delete('./output/*.*'); delete('./output/*');

% get files
dir_input = dir('./input/*.mp4');
if length(dir_input)==0 
    fprintf('\nerror: ./input folder non-existent or no MP4 files found within.\n\n');
    return;
end




for ind_vid=1:length(dir_input)
    
	vid_in = ['./input/' dir_input(ind_vid).name];
    ind_prefix_pos=strfind(lower(vid_in),'/')+1;
    ind_prefix_pos=ind_prefix_pos(end); % keep last slash position + 1
    ind_postfix_pos=strfind(lower(vid_in),'.mp4')-1;
    ind_postfix_pos=ind_postfix_pos(1); % in case many were found
    vid_in_name=vid_in(ind_prefix_pos:ind_postfix_pos);

    fin_test=fopen(vid_in,'rb');
    if fin_test==-1
        fprintf('\nerror: input video %s was not found.\n\n',vid_in);
        return;
    end
    fclose(fin_test);
    


    % transcode each video
    fprintf('\ntranscoding video: %s... ',vid_in);
    for j=1:tot_passes
        fprintf('\tpass %d',j)
        pass_curr_str=['pass' num2str(j) '_'];
        str_trans_pass=[ffmpeg_bin ' -i "' vid_in '" ' char(profile_pass_str(j))];
        if j<tot_passes
            str_trans_pass=[str_trans_pass ' NUL'];
        else
            str_trans_pass=[str_trans_pass ' ./output/"' vid_in_name '_trans.mp4"'];
        end
        [s w]=dos(str_trans_pass);
    end

    fprintf('\tdone.');
end


fprintf('\n\n\n');
status=0;
return;

