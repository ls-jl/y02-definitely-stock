/*
 * Copyright (C) 2017 The Android Open Source Project
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.android.settings.development;

import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.doNothing;
import static org.mockito.Mockito.doReturn;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import android.app.ActivityManager;

import androidx.preference.Preference;
import androidx.preference.PreferenceScreen;

import com.android.settings.applications.ProcStatsData;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import org.robolectric.RobolectricTestRunner;
import org.robolectric.RuntimeEnvironment;

@RunWith(RobolectricTestRunner.class)
public class MemoryUsagePreferenceControllerTest {

    @Mock
    private Preference mPreference;
    @Mock
    private PreferenceScreen mScreen;
    @Mock
    private ProcStatsData mProcStatsData;
    @Mock
    private ProcStatsData.MemInfo mMemInfo;

    private MemoryUsagePreferenceController mController;

    @Before
    public void setup() {
        MockitoAnnotations.initMocks(this);
        mController = spy(new MemoryUsagePreferenceController(RuntimeEnvironment.application));
        doReturn(mProcStatsData).when(mController).getProcStatsData();
        doNothing().when(mController).setDuration();
        when(mScreen.findPreference(mController.getPreferenceKey())).thenReturn(mPreference);
        when(mProcStatsData.getMemInfo()).thenReturn(mMemInfo);
        mController.displayPreference(mScreen);
    }

    @Test
    public void updateState_shouldUpdatePreferenceSummary() {
        mController.updateState(mPreference);

        verify(mPreference).setSummary(anyString());
    }

    @Test
    public void updateState_lowRam_usesRealtimeMemory() {
        final ActivityManager.MemoryInfo realtime = new ActivityManager.MemoryInfo();
        realtime.totalMem = 1024L * 1024L * 1024L;
        realtime.availMem = 400L * 1024L * 1024L;
        doReturn(true).when(mController).isLowRamDevice();
        doReturn(realtime).when(mController).getRealtimeMemoryInfo();

        mController.updateState(mPreference);

        verify(mProcStatsData, never()).refreshStats(true);
        verify(mPreference).setSummary(anyString());
    }
}
