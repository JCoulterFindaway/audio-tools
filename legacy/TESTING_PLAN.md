# Audio Tools Testing Plan

## Overview
Systematic plan to safely understand and test inherited audio tools with misleading names.

## Phase 1: Code Analysis ✅ COMPLETE
- [x] Analyzed actual functionality vs file names
- [x] Identified potential risks and dependencies
- [x] Mapped read-only vs file-modifying operations

## Phase 2: Safe Testing Environment Setup

### Create Testing Directory Structure
```bash
mkdir -p Testing/{input,output,backup}
```

### Prepare Test Audio Files
- Copy 2-3 small audio files to `Testing/input/`
- Create backups in `Testing/backup/`
- Use files you don't mind potentially corrupting

### Environment Isolation
- Run all tests from `Testing/` directory
- Monitor file system changes
- Verify no unintended modifications

## Phase 3: Tool-by-Tool Testing

### SAFE TOOLS (Read-only operations)

#### 3A. Test `scratch.py` - Simple Audio Probe
```bash
# Test with sample file
python3 scratch.py
# Expected: Basic ffmpeg info output
```

#### 3B. Test `passport_opener.py` - Duration Extractor  
```bash
# Test duration extraction
python3 passport_opener.py
# Expected: Duration in seconds for each test file
```

### RISKY TOOLS (File-modifying operations)

#### 3C. Test `onix_opener.py` - Audio Normalizer ⚠️
**CAUTION**: This tool modifies files and creates temps in root directory!

**Before testing:**
1. Create isolated test directory
2. Copy disposable audio files
3. Modify code to use safer temp path

**Test Steps:**
```bash
# 1. Create safe temp directory
mkdir -p Testing/temp

# 2. Modify onix_opener.py line 16:
# FROM: scratch_path: str = '/'  
# TO:   scratch_path: str = './Testing/temp'

# 3. Test with backup file
python3 onix_opener.py
```

**Expected Results:**
- Creates normalized MP3 (44.1kHz, 64k, mono)
- Strips all metadata
- Cleans up temp files

## Phase 4: API Tools Testing

### 4A. Audio Service Client Tools
**CAUTION**: These connect to external services!

#### Check Dependencies First
```bash
pip list | grep -E "(boto3|requests)"
```

#### Test Steps (if dependencies available):
```bash
# Check what these tools do without executing
python3 -c "import audio_service_client; print('Client loads successfully')"
```

**DO NOT RUN** the actual service calls without understanding:
- What service they connect to
- Authentication requirements  
- Potential costs or rate limits

### 4B. Large Analysis Tool
`check_audio_cohort.py` (2,628 lines!)
- **DO NOT RUN** without understanding scope
- Contains hardcoded content IDs
- Likely makes many API calls

## Phase 5: Documentation & Recommendations

### Suggested Renames
| Current Name | Suggested New Name | Reason |
|--------------|-------------------|---------|
| `onix_opener.py` | `audio_normalizer.py` | Actually normalizes audio |
| `passport_opener.py` | `duration_extractor.py` | Extracts track duration |

### Documentation Template
For each tool, document:
- **Actual Purpose**: What it really does
- **Dependencies**: Required packages/tools
- **Input/Output**: What files it expects/creates
- **Safety**: Read-only vs modifying operations
- **Usage Examples**: How to run safely

## Safety Checklist
- [ ] Test in isolated directory
- [ ] Use backup/disposable files
- [ ] Understand external service connections
- [ ] Verify temp file cleanup
- [ ] Check for hardcoded paths
- [ ] Document actual functionality

## Next Steps for Sharing
1. Complete testing and documentation
2. Suggest file renames for clarity
3. Create usage examples
4. Document dependencies and setup
5. Add safety warnings where needed