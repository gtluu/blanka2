library(fuzzyjoin)
library(VGAM)
library(gtools)

combinePeakLists <- function(peakLists, tol) {
  # Merge peak lists based on first peak list.
  for (i in 2:length(peakLists)) {
    if (i == 2) {
      bigDf <- fuzzyjoin::difference_full_join(peakLists[[i-1]],
                                               peakLists[[i]],
                                               by='mz',
                                               max_dist=tol)
    } else {
      bigDf <- fuzzyjoin::difference_full_join(bigDf, peakLists[[i]], by='mz',
                                               max_dist=tol)
    }
    colnames(bigDf)[1] <- 'mz'
  }
  colnames(bigDf) <- as.character(seq(1, ncol(bigDf)))
  
  refDf <- bigDf
  
  finalDfs <- list()
  for (m in seq(1, ncol(bigDf)-2)) {
    # Remove first peak list and get peaks from second peak list that were not
    # merged to first list for merging with subsequent peak lists.
    tmpPeakLists <- list()
    for (i in 2:ncol(refDf)) {
      tmpDf <- as.data.frame(refDf[which(is.na(refDf[, 1])),][, i])
      colnames(tmpDf) <- c('mz')
      tmpDf <- as.data.frame(tmpDf[which(!is.na(tmpDf$mz)),])
      colnames(tmpDf) <- c('mz')
      tmpPeakLists[[length(tmpPeakLists) + 1]] <- tmpDf
    }
    
    # Iteratively merge peak lists based on subsequent peak lists, similar to
    # first merge above.
    for (i in 2:length(tmpPeakLists)) {
      if (i == 2) {
        tmpDf <- fuzzyjoin::difference_full_join(tmpPeakLists[[i-1]],
                                                 tmpPeakLists[[i]],
                                                 by='mz', max_dist=tol)
      } else {
        tmpDf <- fuzzyjoin::difference_full_join(tmpDf, tmpPeakLists[[i]],
                                                 by='mz', max_dist=tol)
      }
      colnames(tmpDf)[1] <- 'mz'
    }
    colnames(tmpDf) <- as.character(seq(1 + m, ncol(bigDf)))
    
    refDf <- tmpDf
    
    # Add columns of NA to match full number of columns in full dataframe of
    # peak lists.
    for (j in 1:m) {
      tmpDf[, as.character(j)] <- rep(NA, nrow(tmpDf))
    }
    
    # Append peak lists to finalDfs list.
    if (m != ncol(bigDf) - 2) {
      finalDfs[[length(finalDfs) + 1]] <- tmpDf[which(!is.na(tmpDf[, 1])),]
    } else {
      finalDfs[[length(finalDfs) + 1]] <- tmpDf
    }
  }
  
  # Concatenate each datafram in list of finalDfs to make final dataframe of
  # combined peak lists.
  for (i in 1:length(finalDfs)) {
    if (i == 1) {
      finalDf <- rbind(bigDf[which(!is.na(bigDf[, 1])),], finalDfs[[i]])
    } else {
      finalDf <- rbind(finalDf, finalDfs[[i]])
    }
  }
  
  return(finalDf)
}

pairwiseCommonPeaks <- function(x, y, tol, cutoff) {
  # Merge peak lists.
  peaks <- fuzzyjoin::difference_full_join(x, y, by='mz', max_dist=tol)
  peaks[is.na(peaks)] <- 0
  
  # Calculate peak similarity scores.
  peaks$score <- 1 - VGAM::erf(abs(peaks$mz.x - peaks$mz.y) / (2 * tol))
  peaks <- peaks[which(peaks$score >= cutoff),]
  
  return(peaks)
}

multipleCommonPeaks <- function(peakLists, tol, cutoff) {
  # Combine peak lists into single large dataframe.
  bigDf <- combinePeakLists(peakLists, tol=tol)
  
  # Calculate pairwise similarity scores for each combination of peak lists.
  listOfScores <- list()
  for (i in 1:ncol(bigDf)) {
    scoresDf <- data.frame(matrix(NA, nrow=nrow(bigDf), ncol=0))
    for (j in 1:ncol(bigDf)) {
      if (i != j) {
        scoresDf[, as.character(j)] <- 1 - VGAM::erf(abs(bigDf[, i] - bigDf[, j]) / (2 * tol))
        scoresDf[is.na(scoresDf)] <- 0
        scoresDf$average <- rowMeans(scoresDf)
      }
    }
    listOfScores[[i]] <- scoresDf
  }
  
  # Average pairwise similarity scores to obtain multiple similarity scores.
  scoresDf <- data.frame(matrix(NA, nrow=nrow(bigDf), ncol=length(listOfScores)))
  colnames(scoresDf) <- seq(1, length(listOfScores))
  for (i in 1:length(listOfScores)) {
    scoresDf[, i] <- listOfScores[[i]]$average
  }
  
  bigDf$score <- rowMeans(scoresDf)
  bigDf <- bigDf[which(bigDf$score >= cutoff),]
  
  return(bigDf)
}

consensusPeakList <- function(peakLists, tol, cutoff) {
  # Combine peak lists into single large dataframe.
  bigDf <- combinePeakLists(peakLists, tol=tol)
  
  # Find how many peak lists each peak was found in and remove if lower than
  # the cutoff.
  bigDf$N <- rowSums(!is.na(bigDf))
  bigDf <- bigDf[which(bigDf$N >= cutoff),]
  
  # Get average m/z values.
  n <- bigDf$N
  bigDf <- subset(bigDf, select=-c(N))
  bigDf$average <- rowMeans(bigDf, na.rm=TRUE)
  bigDf$N <- n
  
  return(bigDf)
}

peaksInCommon <- function(peakLists, sigma, pairwiseCutoff, multipleCutoff,
                          consensusCutoff) {
  # Get all possible combinations of peak lists.
  peakListCombos <- gtools::combinations(n=length(peakLists), r=2,
                                         v=seq(1, length(peakLists)))
  
  # Get dataframes with pairwise similarity scores for each combination of peak
  # lists.
  pairwiseResults <- list()
  for (i in 1:nrow(peakListCombos)) {
    i <- peakListCombos[i,]
    index <- length(pairwiseResults) + 1
    pairwiseResults[[index]] <- pairwiseCommonPeaks(peakLists[[i[1]]],
                                                    peakLists[[i[2]]],
                                                    tol=sigma,
                                                    cutoff=pairwiseCutoff)
  }
  
  # Get dataframe with multiple peak similarity scores for each peak.
  multipleResults <- multipleCommonPeaks(peakLists, tol=sigma,
                                         cutoff=multipleCutoff)
  
  # Get dataframe with consensus peak list.
  consensusResults <- consensusPeakList(peakLists, tol=sigma,
                                        cutoff=consensusCutoff)
  
  return(list('pairwise'=pairwiseResults,
              'multiple'=multipleResults,
              'consensus'=consensusResults))
}
