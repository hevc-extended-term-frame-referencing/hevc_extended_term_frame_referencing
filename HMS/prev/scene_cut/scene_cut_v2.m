function [status] = scene_cut_v2(ffmpeg_bin,ffprobe_bin, thres,max_chunks)
% 
% Scene cut utility function
% [status] = scene_cut_v2(folder_in,folder_out, ffmpeg_bin, ffprobe_bin, thres,max_chunks)
% Parameters:
% ffmpeg_bin:   the binary of ffmpeg
% ffprobe_bin:  the binary of ffprobe
% thres:        scene detection threshold
% max_chunks:   max. number of chunks to cut the file into prior to transcoding
%               the cuts are selected as widely apart as possible in order
%               to create as equally-sized chunks are possible, while at
%               the same time selecting sharp scene cuts to avoid possible
%               artifacts from the separate transcoding process
% Note #1:      All inputs are all MP4 videos within the folder ./input (which
%               is assumed to be in place!)
% Note #2:      All outputs are placed in the folder ./output (which is
%               created if non-existent), within folders having each input
%               video name and a file list "SEG0.mp4", "SEG1.mp4", etc.
%

status=-1; % by default return error code -1 if function does not complete


if max_chunks<2 || thres<0 || thres>1
    fprintf('\nerror: you must have max_chunks>1 and 0<thres<=1\n\n');
    return;
end

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
    
    fprintf('\n\nFile %s found, running ffprobe scene detector with threshold %1.3f ...',vid_in,thres);

    % run the scene-cut detector and select the sharpest <max_chunks> chunks
    [s w]=dos([ffprobe_bin ' -show_frames -of compact=p=0 -f lavfi "movie=' vid_in ',select=gt(scene\,' num2str(thres) ')"']);
    fprintf('\t\tdone.\n');

    fprintf('\nRetrieving segments and determining the best cuts for quasi-equivolume cuts ...');
    % get scene scores
    pos_score_start=regexp(w,'scene_score=')+12;
    if isempty(pos_score_start)
        fprintf('\n\terror: no scene-score values found.\n\n');
        return;
    end
    scene_score=0;
    for i=1:length(pos_score_start)
        pos_score_end=regexp(w(pos_score_start(i):end),'\d.\d*','end');
        scene_score(i)=str2num(w(pos_score_start(i):pos_score_start(i)+pos_score_end(1)));
    end

    % and the corresponding time stamps
    pos_time_start=regexp(w,'pkt_pts_time=')+13;
    if isempty(pos_time_start)
        fprintf('\n\terror: no scene time-stamp values found.\n\n');
        return;
    end
    scene_time=0;
    for i=1:length(pos_time_start)
        pos_time_end=strfind(w(pos_time_start(i):end),'pkt_');
        scene_time(i)=str2num(w(pos_time_start(i):pos_time_start(i)+pos_time_end(1)-3));
    end

    % cut the video into chunks
    if length(scene_time)<max_chunks-1 
        fprintf('\n\twarning: only %d chunks are found, consider reducing <max_chunks> or else transcoding the entire video directly!\n',length(scene_time));
        max_chunks=length(scene_time);
        sel_scene_time=scene_time;
    else
        valid_ind=find(scene_score>=thres);
        if length(valid_ind)<max_chunks-1
            % this means there are only a few scene cuts above the threshold, use these and give a warning
            fprintf('\n\twarning: only %d chunks are found, reduce <max_chunks> or <thres>, or else transcode the entire video directly as there are not enough scene cuts!\n',length(valid_ind)+1);
            sel_scene_time=scene_time(valid_ind);
            max_chunks=length(valid_ind)+1; 
        else    
            % keep only the indices above the threshold
            scene_time=scene_time(valid_ind);
            scene_score=scene_score(valid_ind);
            last_time_stamp=scene_time(end); 
            % this is the desired chunk size (in seconds) based on the last time stamp found
            mean_chunk_size=last_time_stamp/max_chunks;
            found_scene_time=0;
            for i=1:max_chunks-1
                diff_time=abs(scene_time-mean_chunk_size*i); 
                found_scene_time(i)=scene_time(find(diff_time==min(diff_time)));
            end
            % check that we found monotonically-increasing scene-cut timestamps
            % if not, ignore any equal time stamps and warn that less were found
            sel_scene_time=0;
            sel_scene_time(1)=found_scene_time(1);
            j=2;
            for i=2:max_chunks-1
                if found_scene_time(i)>found_scene_time(i-1)
                    sel_scene_time(j)=found_scene_time(i);
                    j=j+1;
                end
            end
            if j<max_chunks
                fprintf('\n\twarning: only %d quasi-equisized chunks found.\n',j);
                max_chunks=j;
            end
        end
    end
    fprintf('\t\tdone.\n\n');

    fprintf('\ncutting video to %d segments at times:\t %s ...',max_chunks,num2str(sel_scene_time(1:end)));
    str_partition=[ffmpeg_bin ' -i "' vid_in '" -y -f segment -segment_times '];
    str_partition=[str_partition num2str(sel_scene_time(1))];
    for i=2:max_chunks-1
        str_partition=[str_partition ',' num2str(sel_scene_time(i))];
    end
    str_partition=[str_partition ' -c:v copy -c:a copy ./output/SEG%d_"' vid_in_name '".mp4'];
    [s w]=dos(str_partition);
    % fprintf('\nFFMPEG output dump: ');
    % fprintf('\n%s\n\n',w); 

    fprintf('\t\tdone.\n\n');
end
status=0;
return;

